from sqladmin import Admin, ModelView
from .models import User, Problem, TestCase, Constraint, Tag, ProblemTag, Solution

def setup_admin(app, engine):
    admin = Admin(app, engine)

    class UserAdmin(ModelView, model=User):
        column_list = [User.id, User.name, User.email, User.provider, User.avatar_url, User.created_at]
        column_searchable_list = [User.name, User.email]
        column_filterable_list = [User.provider, User.name]
        pass

    class ProblemAdmin(ModelView, model=Problem):
        column_list = [Problem.id, Problem.title, Problem.difficulty, Problem.created_at]
        column_searchable_list = [Problem.title]
        column_filterable_list = [Problem.difficulty, Problem.created_at]

    class TestCaseAdmin(ModelView, model=TestCase):
        column_list = [TestCase.id, TestCase.problem_id, TestCase.is_hidden, TestCase.expected_output, TestCase.explanation]
        column_filterable_list = [TestCase.is_hidden, TestCase.problem_id]

    class ConstraintAdmin(ModelView, model=Constraint):
        column_list = [Constraint.id, Constraint.problem_id, Constraint.order, Constraint.created_at]
        column_filterable_list = [Constraint.created_at]

    class TagAdmin(ModelView, model=Tag):
        column_list = [Tag.id, Tag.name]
        column_searchable_list = [Tag.name]

    class ProblemTagAdmin(ModelView, model=ProblemTag):
        column_list = [ProblemTag.problem_id, ProblemTag.tag_id]

    class SolutionAdmin(ModelView, model=Solution):
        column_list = [Solution.id, Solution.user_id, Solution.problem_id, Solution.language, Solution.status, Solution.created_at]
        column_filterable_list = [Solution.language, Solution.status, Solution.created_at]

    admin.add_view(UserAdmin)
    admin.add_view(ProblemAdmin)
    admin.add_view(TestCaseAdmin)
    admin.add_view(ConstraintAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ProblemTagAdmin)
    admin.add_view(SolutionAdmin)