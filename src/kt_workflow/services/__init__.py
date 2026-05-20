"""
领域服务层：复杂逻辑从 nodes 挪到此处，便于单测与团队协作。

契约见 docs/kt_workflow_contracts.md。

为避免与 nodes 的循环导入，请从子模块显式导入，例如：
``from kt_workflow.services.source_extract import extract_from_source_uri``
"""
