"""Tests for the curriculum loader and graph builder."""

from __future__ import annotations

import pytest

from optibench.curriculum import (
    CurriculumError,
    CurriculumGraph,
    CurriculumNode,
    RefResolver,
    load_curriculum,
    resolve_curriculum_path,
)


def _node(id, kind="experiment", ref=None, prereq=None, module="10-foundations"):
    return CurriculumNode(
        id=id,
        kind=kind,
        ref=ref or id,
        title=f"节点 {id}",
        module=module,
        prerequisites=prereq or [],
    )


def _resolver(*ids):
    return RefResolver(experiments=set(ids))


def _write_yaml(tmp_path, text: str):
    path = tmp_path / "curriculum.yaml"
    path.write_text(text, encoding="utf-8")
    return path


class TestLoader:
    def test_valid(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """\
nodes:
  - id: a
    kind: experiment
    ref: a
    title: 实验 A
    module: 10-foundations
    prerequisites: []
  - id: b
    kind: experiment
    ref: b
    title: 实验 B
    prerequisites: [a]
""",
        )
        nodes = load_curriculum(path)
        assert [n.id for n in nodes] == ["a", "b"]
        assert nodes[1].prerequisites == ["a"]
        assert nodes[1].module == ""

    def test_missing_file(self, tmp_path):
        with pytest.raises(CurriculumError, match="不存在"):
            load_curriculum(tmp_path / "curriculum.yaml")

    def test_invalid_yaml(self, tmp_path):
        path = _write_yaml(tmp_path, ": : [")
        with pytest.raises(CurriculumError, match="合法 YAML"):
            load_curriculum(path)

    def test_top_level_must_have_nodes_list(self, tmp_path):
        path = _write_yaml(tmp_path, "foo: bar")
        with pytest.raises(CurriculumError, match="'nodes'"):
            load_curriculum(path)

    def test_missing_required_field(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            "nodes:\n  - id: a\n    kind: experiment\n    title: 实验 A\n",
        )
        with pytest.raises(CurriculumError, match="'ref'"):
            load_curriculum(path)

    def test_invalid_kind(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            "nodes:\n  - id: a\n    kind: quiz\n    ref: a\n    title: A\n",
        )
        with pytest.raises(CurriculumError, match="'kind'"):
            load_curriculum(path)

    def test_duplicate_node_id(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            "nodes:\n"
            "  - {id: a, kind: experiment, ref: a, title: A}\n"
            "  - {id: a, kind: experiment, ref: a, title: A2}\n",
        )
        with pytest.raises(CurriculumError, match="重复"):
            load_curriculum(path)

    def test_dangling_prerequisite(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            "nodes:\n  - {id: a, kind: experiment, ref: a, title: A, prerequisites: [ghost]}\n",
        )
        with pytest.raises(CurriculumError, match="悬空先修"):
            load_curriculum(path)


class TestGraph:
    def test_edges_from_prerequisites(self):
        nodes = [_node("a"), _node("b", prereq=["a"]), _node("c", prereq=["a", "b"])]
        graph = CurriculumGraph.build(nodes, _resolver("a", "b", "c"))
        assert len(graph.edges) == 3
        assert {(e.from_id, e.to_id) for e in graph.edges} == {
            ("a", "b"),
            ("a", "c"),
            ("b", "c"),
        }

    def test_cycle_detected(self):
        nodes = [_node("a", prereq=["c"]), _node("b", prereq=["a"]), _node("c", prereq=["b"])]
        with pytest.raises(CurriculumError, match="环") as exc_info:
            CurriculumGraph.build(nodes, _resolver("a", "b", "c"))
        assert "a" in str(exc_info.value)

    def test_self_cycle_detected(self):
        nodes = [_node("a", prereq=["a"])]
        with pytest.raises(CurriculumError, match="环"):
            CurriculumGraph.build(nodes, _resolver("a"))

    def test_dangling_experiment_ref(self):
        nodes = [_node("a", ref="ghost-experiment")]
        with pytest.raises(CurriculumError, match="悬空引用"):
            CurriculumGraph.build(nodes, _resolver("a"))

    def test_dangling_concept_ref(self):
        nodes = [_node("c1", kind="concept", ref="ghost-concept")]
        resolver = RefResolver(concepts={"real-concept"})
        with pytest.raises(CurriculumError, match="悬空引用"):
            CurriculumGraph.build(nodes, resolver)

    def test_dangling_practice_and_preset_refs(self):
        resolver = RefResolver(presets={"p1"}, practices={"d1"})
        good = [
            _node("p1", kind="preset", ref="p1"),
            _node("d1", kind="practice", ref="d1"),
        ]
        CurriculumGraph.build(good, resolver)  # should not raise
        bad = [_node("d2", kind="practice", ref="ghost-domain")]
        with pytest.raises(CurriculumError, match="悬空引用"):
            CurriculumGraph.build(bad, resolver)


class TestRealCurriculum:
    """The repo's own modules/curriculum.yaml must be valid and complete."""

    def test_builds_against_real_registries(self):
        nodes = load_curriculum(resolve_curriculum_path())
        graph = CurriculumGraph.build(nodes)  # uses real registries
        kinds = {}
        for node in graph.nodes.values():
            kinds.setdefault(node.kind, []).append(node.id)

        # Coverage: 23 experiments, 2 presets, 4 practice domains, indexed concepts.
        assert len(kinds["experiment"]) == 29
        assert sorted(kinds["preset"]) == ["double-slit-breadboard", "single-slit-breadboard"]
        assert sorted(kinds["practice"]) == [
            "industrial",
            "infrared",
            "microscope",
            "photography",
        ]
        assert set(kinds["concept"]) >= {"cmos-fundamentals", "cmos-spectral-response"}

        # Every registered experiment is covered by the graph.
        from optibench.lab import get_registry

        registry_ids = {e.id for e in get_registry().list_experiments()}
        assert registry_ids == set(kinds["experiment"])

    def test_experiment_nodes_mirror_registry_prerequisites(self):
        """Curriculum prerequisites of experiment nodes stay in sync with the
        physically-reviewed declarations in the experiment code."""
        nodes = load_curriculum(resolve_curriculum_path())
        graph = CurriculumGraph.build(nodes)
        from optibench.lab import get_registry

        registry = {e.id: e for e in get_registry().list_experiments()}
        for node in graph.nodes.values():
            if node.kind == "experiment":
                assert sorted(node.prerequisites) == sorted(registry[node.ref].prerequisites), (
                    f"实验 {node.id} 的 curriculum 先修与代码声明不一致"
                )

    def test_path_resolution(self):
        assert resolve_curriculum_path().name == "curriculum.yaml"
        assert resolve_curriculum_path().is_file()
