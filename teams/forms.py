from django import forms


# Bootstrap-style helper: stamps `form-control` on every visible widget.
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()


class TeamSearchForm(BootstrapFormMixin, forms.Form):
    # Single text box used by the team list page.
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Search teams...'}),
    )


class EmailTeamForm(BootstrapFormMixin, forms.Form):
    subject = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}))


class ScheduleMeetingForm(BootstrapFormMixin, forms.Form):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('slack', 'Slack Huddle'),
        ('in_person', 'In Person'),
    ]
    date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
    )
    platform = forms.ChoiceField(choices=PLATFORM_CHOICES)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
