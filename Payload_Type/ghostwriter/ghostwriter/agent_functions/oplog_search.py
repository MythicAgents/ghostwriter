from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class OplogSearchArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                display_name="Search Command",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=False
                )]
            ),
            CommandParameter(
                name="comments",
                display_name="Search Comments",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Search Description",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=3,
                    required=False
                )]
            ),
            CommandParameter(
                name="destIp",
                display_name="Search Destination IP",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
            CommandParameter(
                name="sourceIp",
                display_name="Search Source IP",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=5,
                    required=False
                )]
            ),
            CommandParameter(
                name="tool",
                display_name="Search Tool",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=False
                )]
            ),
            CommandParameter(
                name="userContext",
                display_name="Search User Context",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=7,
                    required=False
                )]
            ),
            CommandParameter(
                name="oplog",
                display_name="oplog ID",
                type=ParameterType.Number,
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=9,
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class OplogSearch(CommandBase):
    cmd = "oplog_search"
    needs_admin = False
    help_cmd = "oplog_search -command sudo -oplog 10"
    description = "Search the oplog for entries"
    version = 2
    author = "@its_a_feature_"
    argument_class = OplogSearchArguments
    supported_ui_features = ["ghostwriter:oplog_search"]
    browser_script = BrowserScript(script_name="oplog_search", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
        )
        searchFields = ["command", "comments", "description", "destIp", "sourceIp", "tool", "userContext"]
        searchParameters = [f"${x}: String!" for x in searchFields if taskData.args.get_arg(x) != ""]
        if taskData.args.get_arg("oplog") > 0:
            searchParameters.append("$oplogId: bigint!")
            logFilter = "{oplog: {_eq: $oplogId}"
        else:
            searchParameters.append("$projectId: bigint!")
            logFilter = "{log: {projectId: {_eq: $projectId}}"
        searchParametersString = ", ".join(searchParameters)
        searchParametersFilter = [f"{x}: {{_ilike: ${x} }}" for x in searchFields if taskData.args.get_arg(x) != ""]
        searchParametersFilterString = ", ".join(searchParametersFilter)

        oplog_search_query = gql(
            f"""
            query oplogSearch({searchParametersString}) {{
                oplogEntry(where: {logFilter}, {searchParametersFilterString}}}, order_by: {{id: desc}}) {{
                    command
                    comments
                    description
                    destIp
                    endDate
                    entryIdentifier
                    extraFields
                    operatorName
                    oplog
                    output
                    sourceIp
                    startDate
                    tool
                    userContext
                    id
              }}
            }}
            """
        )
        try:
            searchQueryValues = {x: f"%{taskData.args.get_arg(x)}%" for x in searchFields if taskData.args.get_arg(x) != "" }
            if taskData.args.get_arg("oplog") > 0:
                searchQueryValues["oplogId"] = taskData.args.get_arg("oplog")
            else:
                searchQueryValues["projectId"] = GhostwriterAPI.get_project_id(taskData)
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=oplog_search_query,
                                                                              variable_values=searchQueryValues)
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
