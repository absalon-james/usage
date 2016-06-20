class SuperTag(dict):

    def __init__(self):
        super(SuperTag, self).__init__()
        self['tag_set'] = set()
        self['tags'] = {}

    def track(self, tag, value):
        """Track the tag and value.
        """
        self['tag_set'].add(tag)
        self['tags'].setdefault(tag, set()).add(value)

    def __str__(self):
        """Custom string value for printing.

        :returns: Customized string.
        :rtype: String
        """
        keys = list(self.get('tag_set', set()))
        keys.sort()

        values = set()
        for tag_set in self.get('tags', {}).values():
            values = values.union(tag_set)
        values = list(values)
        values.sort()

        res = "{}:\n\t{}"
        return res.format(', '.join(keys), '\n\t'.join(values))


class Tracker(dict):
    """Class for tracking all tags."""

    def track(self, tag, value):
        """Tracks the tag and value.

        :param tag: Tag to track
        :type tag: String
        :param value: Value to track
        :type value: Object
        """
        # Case insensitive tag
        i_tag = tag.lower()

        # Super tag dict
        self.setdefault(i_tag, SuperTag()).track(tag, value)

    def __str__(self):
        """Custom string value for printing.

        :returns: Customized string.
        :rtype: String
        """
        return '\nShowing all tags in report:\n{}'.format(
            '\n'.join([str(st) for st in self.values()])
        )


_tracker = Tracker()


def track(tag, value):
    """Tracks the tag with value. Use this to let the module handle tracking.

    :param tag: Tag to track
    :type tag: String
    :param value: Value to track
    :type value: Object
    """
    _tracker.track(tag, value)


def all():
    """Returns tracker dictionary.

    :return: Dictionary with all tags and values
    :rtype: Dict
    """
    return _tracker
