import enum
from rich.console import Console as RichConsole
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree
import sys
from ... import utils
from ... utils import logging_utils

class Status(enum.Enum):
  SUCCESS = ('success', 0, 'green', ':green_circle:')
  FIX = ('fix', 0, 'green', ':green_circle:')
  FAILURE = ('failure', 1, 'yellow', ':yellow_circle:')
  ERROR = ('error', 2, 'red', ':red_circle:')

  def __init__(self, strValue, intValue, color, icon):
    self.string = strValue
    self.ordinal = intValue
    self.color = color
    self.icon = icon

  def __str__(self):
    return self.string

  def max(self, other: "Status"):
    if other.ordinal > self.ordinal:
      return other
    if self == Status.FIX or other == Status.FIX:
      return Status.FIX
    return self

class EnforcementResults:

  def __init__(self, title: str, status: Status = Status.SUCCESS, **kwargs):
    self.title = title
    self.status = status
    self.kwargs = kwargs

    self.children = []

  @property
  def depth(self):
    d = 1 if self.children else 0
    for s in self.children:
      d = d + s.depth
    return d

  def logToConsole(self, format: utils.ResultsFormat = utils.ResultsFormat.TABLE):
    console = RichConsole(width=logging_utils.CONSOLE_WIDTH)

    if format == utils.ResultsFormat.TABLE:
      console.print(self.table)
    if format == utils.ResultsFormat.TREE:
      console.print(self.tree)

  @property
  def table(self) -> RichTable:
    table = RichTable(title=self.title)

    table.add_column('Subject', justify='left')
    table.add_column("Title", justify="left", style="cyan", no_wrap=True)
    table.add_column("Result", justify="right")
    table.add_column("Message", justify="left")

    self._tableRow(table)

    return table

  @property
  def tree(self):
    tree = RichTree(self.title)

    self._treeElement(tree)

    return tree

  def _tableRow(self, table):
    if self.children:
      for c in self.children:
        c._tableRow(table)
    else:
      table.add_row(self.kwargs.get("subject"),
                    self.title,
                    f'[{self.status.color}]{str(self.status)}[/{self.status.color}]',
                    self.kwargs.get('msg'))

  def _treeElement(self, tree):
    branch = tree.add(f'{self.status.icon} {self.title}')
    if self.children:
      for c in self.children:
        c._treeElement(branch)

  def append(self, item):
    item = item if isinstance(item, list) else [item]
    for i in item:
      if i is not None:
        self.children.append(i)
        self.status = self.status.max(i.status)

  def exit(self):
    sys.exit(self.status.ordinal)

  def __iadd__(self, item):
    self.append(item)
    return self

  def __bool__(self):
    return self.status == Status.SUCCESS

  def __len__(self):
    return len(self.children)

  def __getitem__(self, index):
    return self.children[index]

  def __iter__(self):
    return self.children.__iter__()
