from click.testing import CliRunner

from auction.__main__ import register_user


def test_register_user():
    runner = CliRunner()
    result = runner.invoke(
        register_user, ['Bauer', 'Jack', 'bauer@ctu.gov', 'CTU'])

    assert result.exit_code == 0
