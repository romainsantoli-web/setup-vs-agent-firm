"""Tests for firm-cli."""

import os
import tempfile

from firm_cli.main import cli


def test_version(capsys):
    """firm --version prints version."""
    try:
        cli(["--version"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "firm-cli" in out


def test_help(capsys):
    """firm --help prints usage."""
    try:
        cli(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "firm" in out.lower()


def test_no_args(capsys):
    """firm with no args prints help."""
    ret = cli([])
    assert ret == 0


def test_init_dry_run(capsys):
    """firm init --dry-run generates files without writing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli(["init", "--sector", "saas", "--size", "startup", "--output", tmpdir, "--dry-run"])
        assert ret == 0
        # dry-run should NOT write actual files
        agents_dir = os.path.join(tmpdir, ".github", "agents")
        assert not os.path.exists(agents_dir)


def test_init_creates_files():
    """firm init creates the expected file structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli(["init", "--sector", "fintech", "--size", "startup", "--output", tmpdir])
        assert ret == 0

        # Check key files exist
        assert os.path.isfile(os.path.join(tmpdir, "AGENTS.md"))
        assert os.path.isfile(os.path.join(tmpdir, "CLAUDE.md"))
        assert os.path.isfile(os.path.join(tmpdir, "CONTRIBUTING.md"))
        assert os.path.isfile(os.path.join(tmpdir, ".vscode", "settings.json"))
        assert os.path.isfile(os.path.join(tmpdir, ".github", "agents", "firm-ceo.agent.md"))
        assert os.path.isfile(os.path.join(tmpdir, ".github", "prompts", "firm-delivery.prompt.md"))
        assert os.path.isfile(os.path.join(tmpdir, "scripts", "install-skills.sh"))
        assert os.path.isfile(os.path.join(tmpdir, "mcp-config.json"))


def test_init_startup_has_4_dept_agents():
    """Startup size generates exactly 4 department agents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "generic", "--size", "startup", "--output", tmpdir])
        agents_dir = os.path.join(tmpdir, ".github", "agents")
        agent_files = [f for f in os.listdir(agents_dir) if f.startswith("department-")]
        assert len(agent_files) == 4


def test_init_enterprise_has_18_dept_agents():
    """Enterprise size generates 18 department agents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "generic", "--size", "enterprise", "--output", tmpdir])
        agents_dir = os.path.join(tmpdir, ".github", "agents")
        agent_files = [f for f in os.listdir(agents_dir) if f.startswith("department-")]
        assert len(agent_files) == 18


def test_init_fintech_install_script_has_skill():
    """Fintech sector install script includes firm-fintech-pack."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "fintech", "--output", tmpdir])
        script = os.path.join(tmpdir, "scripts", "install-skills.sh")
        content = open(script).read()
        assert "firm-fintech-pack" in content


def test_init_generic_install_script_no_sector_skill():
    """Generic sector install script has no sector-specific skill."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "generic", "--output", tmpdir])
        script = os.path.join(tmpdir, "scripts", "install-skills.sh")
        content = open(script).read()
        # Should not have any sector pack
        assert "firm-legal-pack" not in content
        assert "firm-fintech-pack" not in content


def test_init_claude_md_contains_sector():
    """CLAUDE.md mentions the sector."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "medtech", "--output", tmpdir])
        content = open(os.path.join(tmpdir, "CLAUDE.md")).read()
        assert "medtech" in content


def test_init_force_overwrites():
    """firm init --force overwrites existing files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cli(["init", "--sector", "saas", "--output", tmpdir])
        cli(["init", "--sector", "legal", "--output", tmpdir, "--force"])
        content = open(os.path.join(tmpdir, "AGENTS.md")).read()
        assert "legal" in content.lower()


def test_all_15_sectors_generate():
    """All 15 sectors can generate without error."""
    sectors = [
        "generic", "legal", "medtech", "ecommerce", "fintech", "saas",
        "manufacturing", "education", "realestate", "logistics",
        "media", "automotive", "energy", "hr", "consulting",
    ]
    for sector in sectors:
        with tempfile.TemporaryDirectory() as tmpdir:
            ret = cli(["init", "--sector", sector, "--output", tmpdir])
            assert ret == 0, f"Sector {sector} failed"


def test_config_show(capsys):
    """firm config show prints current config."""
    ret = cli(["config", "show"])
    assert ret == 0


def test_memory_no_claude_md(capsys, tmp_path, monkeypatch):
    """firm memory status without CLAUDE.md returns 1."""
    monkeypatch.chdir(tmp_path)
    ret = cli(["memory", "status"])
    assert ret == 1
