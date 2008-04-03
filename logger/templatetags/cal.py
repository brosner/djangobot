import datetime
import calendar
from calendar import Calendar, month_name, day_abbr

from django import template
from logger.models import Message

register = template.Library()

class CalendarNode(template.Node):
    def __init__(self, date, channel):
        self.date = template.Variable(date)
        self.channel = template.Variable(channel)
    
    def render(self, context):
        date = self.date.resolve(context)
        channel = self.channel.resolve(context)
        message_list = Message.objects.filter(logged__year=date.year, logged__month=date.month, channel=channel).dates('logged', 'day')
        c = HTMLFormatCalendar(message_list, channel)
        return c.formatmonth(date.year, date.month)


def do_calendar(parser, token):
    """
    Retrieves the objects from a given model, in that
    model's default ordering, and renders a calendar for the specified
    month in the specified channel.
    
    Syntax::
    
        {% display_calendar for [date] in [channelname] %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes five arguments" % bits[0])
    if bits [1] != 'for':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'for'" % bits[0])
    if bits [3] != 'in':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'in'" % bits[0])
    return CalendarNode(bits[2], bits[4])
    
register.tag('display_calendar', do_calendar)

class HTMLFormatCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes for the day <td>s
    cssclasses = {'table_class': 'calendar',
                  'month_name_class': 'monthName',
                  'other_month_class': 'otherMonth',
                  'day_name_class': 'dayName',
                  'day_class': 'day',
                  'today_class': 'specialDay'
                 }
    
    def __init__(self, event_list, channel):
        self.event_list = event_list
        self.channel = channel
        Calendar.__init__(self)
    
    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="%s">&nbsp;</td>' % (self.cssclasses['other_month_class'],) # day outside month
        else:
            class_style = self.cssclasses['day_class']
            if day == datetime.datetime.today().day:
                class_style = self.cssclasses['today_class']
            
            for e in self.event_list:
                if e.day == day:
                    return '<td class="%s"><a href="%s%s/">%d</a></td>' % (class_style, self.channel.get_absolute_url(), e.strftime("%Y/%m/%d"), day,)
            return '<td class="%s">%d</td>' % (class_style, day)

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th>%s</th>' % (day_abbr[day],)

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr class="%s">%s</tr>' % (self.cssclasses['day_name_class'], s,)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr class="%s"><th colspan="7">%s</th></tr>' % (self.cssclasses['month_name_class'], s)

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="%s">' % (self.cssclasses['table_class']))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        """
        Return a formatted year as a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        for i in xrange(January, January+12, width):
            # months in this row
            months = xrange(i, min(i+width, 13))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>')
            a('</tr>')
        a('</table>')
        return ''.join(v)

    def formatyearpage(self, theyear, width=3, css='css', encoding=None):
        """
        Return a formatted year as a complete HTML page.
        """
        if encoding is None:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a('<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % encoding)
        if css is not None:
            a('<link rel="stylesheet" type="text/css" href="%s" />\n' % css)
        a('<title>Calendar for %d</title\n' % theyear)
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(theyear, width))
        a('</body>\n')
        a('</html>\n')
        return ''.join(v).encode(encoding, "xmlcharrefreplace")
