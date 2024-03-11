from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class FindingsSearchArguments(TaskArguments):

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
            CommandParameter(
                name="description",
                display_name="Search Description",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class FindingsSearch(CommandBase):
    cmd = "findings_search"
    needs_admin = False
    help_cmd = "findings_search -description sudo"
    description = "Search the findings library based on the title and description"
    version = 2
    author = "@its_a_feature_"
    argument_class = FindingsSearchArguments
    supported_ui_features = ["ghostwriter:findings_search"]
    browser_script = BrowserScript(script_name="findings_search", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f"-title \"{taskData.args.get_arg('title')}\" -description \"{taskData.args.get_arg('description')}\""
        )
        findings_search_query = gql(
            """
            query findingsSearch($description: String!, $title: String!) {
              finding(where: {_or: [{description: {_ilike: $description}, title: {_ilike: $title}}]}) {
                id
                title
                description
                severity {
                  severity
                  color
                }
                cvssScore
                type {
                  findingType
                }
              }
            }
            """
        )
        try:
            title = "%" + taskData.args.get_arg("title") + "%"
            if title == "%%":
                title = "%_%"
            description = "%" + taskData.args.get_arg("description") + "%"
            if description == "%%":
                description = "%_%"
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=findings_search_query,
                                                                              variable_values={"title": title,
                                                                                               "description": description})
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
