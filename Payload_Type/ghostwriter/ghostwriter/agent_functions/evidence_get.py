from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class EvidenceGetArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="title",
                display_name="Report Title",
                type=ParameterType.String,
                description="If there are multiple reports, specify which report to get the findings for (uses case insensitive matching)",
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


class EvidenceGet(CommandBase):
    cmd = "evidence_get"
    needs_admin = False
    help_cmd = "evidence_get -title Penetration"
    description = "Get all the evidence associated with a specific report"
    version = 2
    author = "@its_a_feature_"
    argument_class = EvidenceGetArguments
    supported_ui_features = ["ghostwriter:evidence_get"]
    browser_script = BrowserScript(script_name="evidence_get", author="@its_a_feature_")
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
        if taskData.args.get_arg("title") == "":
            response.DisplayParams = ""
        evidence_get_query = gql(
            """
            query findingsGetForReport($title: String!, $projectId: bigint!) {
              evidence(where: {_or: [{finding: {report: {title: {_ilike: $title}, projectId: {_eq: $projectId}}}}, {report: {title: {_ilike: $title}, projectId: {_eq: $projectId}}}]} , order_by: {id: desc}) {
                caption
                description
                document
                findingId
                friendlyName
                id
                uploadDate
                uploadedById
                user {
                  username
                }
                report {
                    title
                }
                finding {
                  title
                  report {
                    title
                  }
                }
              }
            }
            """
        )
        try:
            title = "%" + taskData.args.get_arg("title") + "%"
            if title == "%%":
                title = "%_%"
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=evidence_get_query,
                                                                              variable_values={"title": title,
                                                                                               "projectId": GhostwriterAPI.get_project_id(taskData=taskData)})
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
