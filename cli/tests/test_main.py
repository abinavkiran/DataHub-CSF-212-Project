from click.testing import CliRunner
from cli.main import push

def test_push_command():
    runner = CliRunner()
    result = runner.invoke(push)
    assert result.exit_code == 0
    assert "Pushing data..." in result.output
