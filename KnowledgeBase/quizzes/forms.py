from django import forms

class QuizAttemptForm(forms.Form):
    def __init__(self, *args, quiz=None, **kwargs):
        super().__init__(*args, **kwargs)

        for question in quiz.questions.all():
            self.fields[f'question_{question.id}'] = forms.ModelChoiceField(
                queryset = question.options.all(),
                widget = forms.RadioSelect,
                label = question.question,
                required = True,
            )