"""Tests for the content contract validator and content index."""

from __future__ import annotations

import pytest

from optibench.content.contract import (
    ContractError,
    parse_concept_file,
    split_frontmatter,
    validate_concept,
)
from optibench.content.index import ContentIndex

VALID_FRONTMATTER = """\
---
id: test-concept
title: 测试概念
module: 10-foundations
difficulty: foundation
prerequisites: []
linked_experiments:
  - thin-lens
status: draft
---

## 正文

内容。
"""


def _write(root, rel: str, text: str):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestSplitFrontmatter:
    def test_valid(self):
        data, body = split_frontmatter(VALID_FRONTMATTER, "test.md")
        assert data["id"] == "test-concept"
        assert body.startswith("## 正文")

    def test_missing_frontmatter(self):
        with pytest.raises(ContractError, match="缺少 frontmatter"):
            split_frontmatter("# 没有 frontmatter", "test.md")

    def test_unterminated_frontmatter(self):
        with pytest.raises(ContractError, match="未闭合"):
            split_frontmatter("---\nid: x\ntitle: y\n", "test.md")

    def test_invalid_yaml(self):
        with pytest.raises(ContractError, match="合法 YAML"):
            split_frontmatter("---\n: : [\n---\nbody", "test.md")

    def test_non_mapping_frontmatter(self):
        with pytest.raises(ContractError, match="YAML 映射"):
            split_frontmatter("---\n- just\n- a\n- list\n---\nbody", "test.md")


class TestValidateConcept:
    def _valid_data(self):
        return {
            "id": "test-concept",
            "title": "测试概念",
            "module": "10-foundations",
            "difficulty": "foundation",
            "prerequisites": [],
            "linked_experiments": [],
            "status": "draft",
        }

    def test_valid(self):
        meta = validate_concept(self._valid_data(), "test.md")
        assert meta.id == "test-concept"
        assert meta.difficulty == "foundation"

    def test_missing_fields_lists_them(self):
        data = self._valid_data()
        del data["module"]
        del data["difficulty"]
        with pytest.raises(ContractError, match="module") as exc_info:
            validate_concept(data, "test.md")
        assert "difficulty" in str(exc_info.value)
        assert "test.md" in str(exc_info.value)

    def test_invalid_difficulty(self):
        data = self._valid_data()
        data["difficulty"] = "expert"
        with pytest.raises(ContractError, match="difficulty"):
            validate_concept(data, "test.md")

    def test_invalid_status(self):
        data = self._valid_data()
        data["status"] = "archived"
        with pytest.raises(ContractError, match="status"):
            validate_concept(data, "test.md")

    def test_empty_id(self):
        data = self._valid_data()
        data["id"] = "  "
        with pytest.raises(ContractError, match="'id'"):
            validate_concept(data, "test.md")

    def test_prerequisites_must_be_string_list(self):
        data = self._valid_data()
        data["prerequisites"] = "not-a-list"
        with pytest.raises(ContractError, match="prerequisites"):
            validate_concept(data, "test.md")

    def test_extra_fields_allowed(self):
        data = self._valid_data()
        data["source"] = "https://example.com"
        meta = validate_concept(data, "test.md")
        assert meta.model_extra["source"] == "https://example.com"


class TestContentIndex:
    def test_build_indexes_learning_docs(self, tmp_path):
        _write(tmp_path, "10-foundations/learning/a.md", VALID_FRONTMATTER)
        # Non-tutorial docs must be skipped even with valid-looking frontmatter.
        _write(
            tmp_path,
            "10-foundations/projects/README.md",
            "---\nid: projects.foundations\ntitle: 项目清单\nstatus: draft\n---\n\n# 项目\n",
        )
        _write(tmp_path, "10-foundations/README.md", "# 模块甲\n")
        index = ContentIndex.build(tmp_path)
        assert [m.id for m in index.list_concepts()] == ["test-concept"]
        assert index.errors == []

    def test_get_body(self, tmp_path):
        _write(tmp_path, "10-foundations/learning/a.md", VALID_FRONTMATTER)
        index = ContentIndex.build(tmp_path)
        body = index.get_body("test-concept")
        assert body.startswith("## 正文")
        assert index.get_body("missing") is None

    def test_invalid_frontmatter_collected_not_raised(self, tmp_path):
        _write(tmp_path, "10-foundations/learning/bad.md", "# 无 frontmatter\n")
        _write(tmp_path, "10-foundations/learning/good.md", VALID_FRONTMATTER)
        index = ContentIndex.build(tmp_path)
        assert [m.id for m in index.list_concepts()] == ["test-concept"]
        assert len(index.errors) == 1
        assert "缺少 frontmatter" in index.errors[0].error

    def test_strict_mode_raises(self, tmp_path):
        _write(tmp_path, "10-foundations/learning/bad.md", "# 无 frontmatter\n")
        with pytest.raises(ContractError):
            ContentIndex.build(tmp_path, strict=True)

    def test_duplicate_id_rejected(self, tmp_path):
        _write(tmp_path, "10-foundations/learning/a.md", VALID_FRONTMATTER)
        _write(
            tmp_path,
            "20-geometric-optics/learning/b.md",
            VALID_FRONTMATTER.replace("module: 10-foundations", "module: 20-geometric-optics"),
        )
        with pytest.raises(ContractError, match="重复"):
            ContentIndex.build(tmp_path, strict=True)

    def test_module_mismatch_rejected(self, tmp_path):
        _write(tmp_path, "20-geometric-optics/learning/a.md", VALID_FRONTMATTER)
        with pytest.raises(ContractError, match="不一致"):
            ContentIndex.build(tmp_path, strict=True)

    def test_missing_root_yields_empty_index(self, tmp_path):
        index = ContentIndex.build(tmp_path / "does-not-exist")
        assert index.list_concepts() == []
        assert index.errors == []

    def test_parse_concept_file_roundtrip(self, tmp_path):
        path = _write(tmp_path, "10-foundations/learning/a.md", VALID_FRONTMATTER)
        meta, body = parse_concept_file(path)
        assert meta.linked_experiments == ["thin-lens"]
        assert "内容" in body


class TestRealModules:
    """The repo's own modules/ content must satisfy the contract."""

    def test_repo_modules_build_cleanly(self):
        from optibench.content.loader import resolve_modules_root

        index = ContentIndex.build(resolve_modules_root(), strict=True)
        ids = {m.id for m in index.list_concepts()}
        assert "cmos-fundamentals" in ids
        assert "cmos-spectral-response" in ids
