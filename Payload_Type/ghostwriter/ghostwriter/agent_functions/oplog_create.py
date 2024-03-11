from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class OplogCreateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                display_name="Command",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=False
                )]
            ),
            CommandParameter(
                name="comments",
                display_name="Comments",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Description",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=3,
                    required=False
                )]
            ),
            CommandParameter(
                name="destIp",
                display_name="Destination IP",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
            CommandParameter(
                name="sourceIp",
                display_name="Source IP",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=5,
                    required=False
                )]
            ),
            CommandParameter(
                name="tool",
                display_name="Tool",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=False
                )]
            ),
            CommandParameter(
                name="userContext",
                display_name="User Context",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=7,
                    required=False
                )]
            ),
            CommandParameter(
                name="extraFields",
                display_name="Extra Fields",
                description="Each entry is an extra field in the format `key: value`",
                type=ParameterType.Array,
                default_value=[],
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=8,
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
                    required=True
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class OplogCreate(CommandBase):
    cmd = "oplog_create"
    needs_admin = False
    help_cmd = "oplog_create -command sudo"
    description = "Search the oplog for entries"
    version = 2
    author = "@its_a_feature_"
    argument_class = OplogCreateArguments
    supported_ui_features = ["ghostwriter:oplog_create"]
    browser_script = BrowserScript(script_name="oplog_create", author="@its_a_feature_")
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
        searchParameters = [f"${x}: String!" for x in searchFields]
        searchParameters.append("$oplog: bigint!")
        searchParameters.append("$extraFields: jsonb!")
        searchParametersString = ", ".join(searchParameters)

        searchParametersFilter = [f"{x}: ${x}" for x in searchFields]
        searchParametersFilter.append("oplog: $oplog")
        searchParametersFilter.append("extraFields: $extraFields")

        searchParametersFilterString = ", ".join(searchParametersFilter)
        oplog_search_query = gql(
            f"""
            mutation oplogCreate({searchParametersString}) {{
                insert_oplogEntry_one(object: {{ {searchParametersFilterString} }}) {{
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
              }}
            }}
            """
        )
        try:
            searchQueryValues = {x: f"{taskData.args.get_arg(x)}" for x in searchFields}
            searchQueryValues["oplog"] = taskData.args.get_arg("oplog")
            searchQueryValues["extraFields"] = {}
            for x in taskData.args.get_arg("extraFields"):
                fieldPieces = x.split(":")
                if len(fieldPieces) > 1:
                    searchQueryValues["extraFields"][fieldPieces[0]] = ":".join(fieldPieces[1:]).strip()
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
