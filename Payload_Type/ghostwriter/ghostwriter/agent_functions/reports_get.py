from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ReportsGetArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="title",
                display_name="Search Title",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ReportsGetSearch(CommandBase):
    cmd = "reports_get"
    needs_admin = False
    help_cmd = "reports_get -title penetration"
    description = "Search the current project's reports by title"
    version = 1
    author = "@its_a_feature_"
    argument_class = ReportsGetArguments
    supported_ui_features = ["ghostwriter:reports_get"]
    browser_script = BrowserScript(script_name="reports_get", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f"-title \"{taskData.args.get_arg('title')}\""
        )
        try:
            reports_query = gql(
                """
                query getReports($title: String!, $projectId: bigint!){
                    report(where: {projectId: {_eq: $projectId}, complete: {_eq: false}, archived: {_eq: false}, title: {_ilike: $title}}) {
                        id
                        title
                      }
                }
                """
            )
            search_title = "%" + taskData.args.get_arg("title") + "%"
            if search_title == "%%":
                search_title = "%_%"
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData, query=reports_query,
                                                                              variable_values={
                                                                                  "projectId": GhostwriterAPI.get_project_id(
                                                                                      taskData=taskData),
                                                                                  "title": search_title
                                                                              })
            return await GhostwriterAPI.process_standard_response(response_code=response_code,
                                                                  response_data=response_data,
                                                                  taskData=taskData,
                                                                  response=response)

        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Ghostwriter Access Error"
            response.Success = False
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
