"""Curriculum graph — builds the DAG from loaded nodes.

Provides cycle detection and dangling-reference detection: every node ``ref``
must resolve against the lab experiment registry (``experiment``), the
practice registry (``preset`` / ``practice``), or the content index
(``concept``).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from optibench.curriculum.loader import CurriculumError, CurriculumNode


@dataclass
class CurriculumEdge:
    """Directed edge from a prerequisite node to its dependent node."""

    from_id: str
    to_id: str


@dataclass
class RefResolver:
    """Sets of valid refs per node kind (injectable for tests)."""

    experiments: set[str] = field(default_factory=set)
    presets: set[str] = field(default_factory=set)
    practices: set[str] = field(default_factory=set)
    concepts: set[str] = field(default_factory=set)
    assessments: set[str] = field(default_factory=set)

    @classmethod
    def from_registries(cls) -> RefResolver:
        """Build the resolver from the real registries / content index."""
        from optibench.content import get_content_index, get_quiz_index
        from optibench.lab import get_registry
        from optibench.practice import get_practice_registry

        practice = get_practice_registry()
        return cls(
            experiments={e.id for e in get_registry().list_experiments()},
            presets={a.id for a in practice.list("preset")},
            practices={a.id for a in practice.list("domain")},
            concepts={m.id for m in get_content_index().list_concepts()},
            assessments={q.id for q in get_quiz_index().list_quizzes()},
        )


@dataclass
class CurriculumGraph:
    nodes: dict[str, CurriculumNode]
    edges: list[CurriculumEdge]

    @classmethod
    def build(
        cls,
        nodes: list[CurriculumNode],
        resolver: RefResolver | None = None,
    ) -> CurriculumGraph:
        """Build the graph, validating refs and acyclicity.

        With ``resolver=None`` the real registries are used.
        """
        if resolver is None:
            resolver = RefResolver.from_registries()

        node_map = {node.id: node for node in nodes}
        valid_refs = {
            "concept": resolver.concepts,
            "experiment": resolver.experiments,
            "preset": resolver.presets,
            "practice": resolver.practices,
            "assessment": resolver.assessments,
        }
        for node in nodes:
            if node.kind == "concept" and node.source == "vault":
                continue  # 知识库理论节点（ADR-004）：ref 由前端链接表解析
            if node.ref not in valid_refs[node.kind]:
                raise CurriculumError(
                    f"节点 {node.id!r}（kind={node.kind}）的 ref {node.ref!r} "
                    f"无法解析（悬空引用）"
                )

        edges = [
            CurriculumEdge(from_id=prereq, to_id=node.id)
            for node in nodes
            for prereq in node.prerequisites
        ]
        graph = cls(nodes=node_map, edges=edges)
        graph._check_acyclic()
        return graph

    def _check_acyclic(self) -> None:
        """Kahn's algorithm; raises CurriculumError naming the cycle members."""
        indegree = {node_id: 0 for node_id in self.nodes}
        dependents: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            indegree[edge.to_id] += 1
            dependents[edge.from_id].append(edge.to_id)

        queue = [node_id for node_id, deg in indegree.items() if deg == 0]
        processed = 0
        while queue:
            node_id = queue.pop()
            processed += 1
            for dependent in dependents[node_id]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)
        if processed < len(self.nodes):
            cycle_members = sorted(n for n, deg in indegree.items() if deg > 0)
            raise CurriculumError(
                f"curriculum 存在先修环，涉及节点：{', '.join(cycle_members)}"
            )

    def prerequisites_of(self, node_id: str) -> list[str]:
        return list(self.nodes[node_id].prerequisites)
