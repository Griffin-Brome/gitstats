from .GithubConnection import GithubConnection
from .StatsCollector import StatsCollector
from .PullRequestRepository import PullRequestRepository
from .StatsCalculator import StatsCalculator
from .Reporter import Reporter
from .Templater import Templater


def report(access_token, group_name, repository, start=None, end=None):
    connection = GithubConnection(access_token, repository)
    repository = PullRequestRepository(connection.get_repository())
    collector = StatsCollector(repository, start=start, end=end)
    calculator = StatsCalculator(collector)

    templater = Templater()

    reporter = Reporter(group_name, templater.get_template(), calculator)

    print(reporter.report())
