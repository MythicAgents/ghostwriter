from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ProjectNotesUpdateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="note_id",
                default_value=0,
                description="ID of the project note to delete",
                type=ParameterType.Number,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=0
                )]
            ),
            CommandParameter(
                name="note",
                default_value="",
                description="Final Note to save",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1
                )]
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ProjectNotesUpdate(CommandBase):
    cmd = "project_notes_update"
    needs_admin = False
    help_cmd = "project_notes_edit"
    description = "Update a note on a project"
    version = 1
    author = "@its_a_feature_"
    argument_class = ProjectNotesUpdateArguments
    supported_ui_features = ["ghostwriter:project_notes_update"]
    browser_script = BrowserScript(script_name="project_notes_update", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f""
        )
        try:
            edit_project_note = gql(
                """
                mutation updateProjectNote($note_id: bigint!, $note: String!){
                    update_projectNote_by_pk(pk_columns: {id: $note_id}, _set: {note: $note}) {
                        id
                        note
                    }
                }
                """
            )
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData, query=edit_project_note,
                                                                              variable_values={
                                                                                  "note_id": taskData.args.get_arg("note_id"),
                                                                                  "note": taskData.args.get_arg("note")
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
