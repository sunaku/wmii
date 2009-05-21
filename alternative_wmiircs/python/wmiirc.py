import operator
import os
import re
import sys
import traceback

import pygmi
from pygmi import *
from pygmi import events

identity = lambda k: k

# Keys
events.keydefs = dict(
    mod='Mod4',
    left='h',
    down='j',
    up='k',
    right='l')

# Bars
noticetimeout=5
noticebar=('right', '!notice')

# Theme
background = '#333333'
floatbackground='#222222'

wmii['font'] = 'drift,-*-fixed-*-*-*-*-9-*-*-*-*-*-*-*'
wmii['normcolors'] = '#000000', '#c1c48b', '#81654f'
wmii['focuscolors'] = '#000000', '#81654f', '#000000'
wmii['grabmod'] = events.keydefs['mod']
wmii['border'] = 2

def setbackground(color):
    call('xsetroot', '-solid', color)
setbackground(background)

terminal = 'wmiir', 'setsid', 'xterm'
pygmi.shell = os.environ.get('SHELL', 'sh')

@defmonitor
def load(self):
    return re.sub(r'^.*: ', '', call('uptime')).replace(', ', ' ')
@defmonitor
def time(self):
    from datetime import datetime
    return datetime.now().strftime('%c')

wmii.colrules = (
    ('gimp', '17+83+41'),
    ('.*', '62+38 # Golden Ratio'),
)

wmii.tagrules = (
    ('MPlayer|VLC', '~'),
)

def unresponsive_client(client):
    msg = 'The following client is not responding. What would you like to do?'
    resp = call('wihack', '-transient', client.id,
                'xmessage', '-nearmouse', '-buttons', 'Kill,Wait', '-print',
                '%s\n  %s' % (client, client.label))
    if resp == 'Kill':
        client.slay()

# End Configuration

client.awrite('/event', 'Start wmiirc')

tags = Tags()
bind_events({
    'Quit':         lambda args: sys.exit(),
    'Start':        lambda args: args == 'wmiirc' and sys.exit(),
    'CreateTag':    tags.add,
    'DestroyTag':   tags.delete,
    'FocusTag':     tags.focus,
    'UnfocusTag':   tags.unfocus,
    'UrgentTag':    lambda args: tags.set_urgent(args.split()[1], True),
    'NotUrgentTag': lambda args: tags.set_urgent(args.split()[1], False),

    'AreaFocus':    lambda args: (args == '~' and
                                  (setbackground(floatbackground), True) or
                                  setbackground(background)),

    'Unresponsive': lambda args: Thread(target=unresponsive_client,
                                        args=(Client(args),)).start(),

    'Notice':       lambda args: notice.show(args),

    ('LeftBarClick', 'LeftBarDND'):
        lambda args: args.split()[0] == '1' and tags.select(args.split(' ', 1)[1]),

    'ClientMouseDown':  lambda args: menu(*args.split(), type='client'),
    'LeftBarMouseDown': lambda args: menu(*reversed(args.split()), type='lbar'),
})

@apply
class Actions(events.Actions):
    def rehash(self, args=''):
        program_menu.choices = program_list(os.environ['PATH'].split(':'))
    def quit(self, args=''):
        wmii.ctl('quit')
    def eval_(self, args=''):
        exec args
    def exec_(self, args=''):
        wmii['exec'] = args
    def exit(self, args=''):
        client.awrite('/event', 'Quit')

program_menu = Menu(histfile='%s/history.prog' % confpath[0], nhist=5000,
                    action=curry(call, 'wmiir', 'setsid',
                                 pygmi.shell, '-c', background=True))
action_menu = Menu(histfile='%s/history.action' % confpath[0], nhist=500,
                   choices=lambda: Actions._choices,
                   action=Actions._call)
tag_menu = Menu(histfile='%s/history.tags' % confpath[0], nhist=100,
                choices=lambda: sorted(tags.tags.keys()))

def menu(target, button, type):
    MENUS = {
        ('client', '3'): (
            ('Delete',     lambda c: Client(c).kill()),
            ('Kill',       lambda c: Client(c).slay()),
            ('Fullscreen', lambda c: Client(c).set('Fullscreen', 'on'))),
        ('lbar', '3'): (
            ('Delete',     lambda t: Tag(t).delete())),
    }
    choices = MENUS.get((type, button), None)
    if choices:
        ClickMenu(choices=(k for k, v in choices),
                  action=lambda k: dict(choices).get(k, identity)(target)
                 ).call()

class Notice(Button):
    def __init__(self):
        super(Notice, self).__init__(*noticebar)
        self.timer = None

    def tick(self):
        self.label = ''

    def write(self, notice):
        client.awrite('/event', 'Notice %s' % notice.replace('\n', ' '))

    def show(self, notice):
        if self.timer:
            self.timer.cancel()
        self.label = notice
        from threading import Timer
        self.timer = Timer(noticetimeout, self.tick)
        self.timer.start()
notice = Notice()

bind_keys({
    '%(mod)s-Control-t': lambda k: events.toggle_keys(restore='%(mod)s-Control-t'),

    '%(mod)s-%(left)s':  lambda k: Tag('sel').select('left'),
    '%(mod)s-%(right)s': lambda k: Tag('sel').select('right'),
    '%(mod)s-%(up)s':    lambda k: Tag('sel').select('up'),
    '%(mod)s-%(down)s':  lambda k: Tag('sel').select('down'),

    '%(mod)s-Control-%(up)s':   lambda k: Tag('sel').select('up', stack=True),
    '%(mod)s-Control-%(down)s': lambda k: Tag('sel').select('down', stack=True),

    '%(mod)s-space': lambda k: Tag('sel').select('toggle'),

    '%(mod)s-Shift-%(left)s':  lambda k: Tag('sel').send(Client('sel'), 'left'),
    '%(mod)s-Shift-%(right)s': lambda k: Tag('sel').send(Client('sel'), 'right'),
    '%(mod)s-Shift-%(up)s':    lambda k: Tag('sel').send(Client('sel'), 'up'),
    '%(mod)s-Shift-%(down)s':  lambda k: Tag('sel').send(Client('sel'), 'down'),

    '%(mod)s-Shift-space':  lambda k: Tag('sel').send(Client('sel'), 'toggle'),

    '%(mod)s-d': lambda k: setattr(Tag('sel').selcol, 'mode', 'default-max'),
    '%(mod)s-s': lambda k: setattr(Tag('sel').selcol, 'mode', 'stack-max'),
    '%(mod)s-m': lambda k: setattr(Tag('sel').selcol, 'mode', 'stack+max'),

    '%(mod)s-f':       lambda k: Client('sel').set('Fullscreen', 'toggle'),
    '%(mod)s-Shift-c': lambda k: Client('sel').kill(),

    '%(mod)s-a': lambda k: action_menu.call(),
    '%(mod)s-p': lambda k: program_menu.call(),

    '%(mod)s-Return': lambda k: call(*terminal, background=True),

    '%(mod)s-t':       lambda k: tags.select(tag_menu.call()),
    '%(mod)s-Shift-t': lambda k: setattr(Client('sel'), 'tags', tag_menu.call()),

    '%(mod)s-n': lambda k: tags.select(tags.next()),
    '%(mod)s-b': lambda k: tags.select(tags.next(True)),
    '%(mod)s-i': lambda k: tags.select(tags.NEXT),
    '%(mod)s-o': lambda k: tags.select(tags.PREV),
})
def bind_num(i):
    bind_keys({
        '%%(mod)s-%d' % i:       lambda k: tags.select(str(i)),
        '%%(mod)s-Shift-%d' % i: lambda k: setattr(Client('sel'), 'tags', i),
    })
map(bind_num, range(0, 10))

Actions.rehash()

dirs = ('%s/plugins' % dir for dir in confpath if os.access('%s/plugins' % dir, os.R_OK))
files = filter(re.compile(r'\.py$').match,
               reduce(operator.add, map(os.listdir, dirs), []))
for f in ['wmiirc_local'] + ['plugins.%s' % file[:-3] for file in files]:
    try:
        exec 'import %s' % f
    except Exception, e:
        traceback.print_exc(sys.stdout)

event_loop()

# vim:se sts=4 sw=4 et: