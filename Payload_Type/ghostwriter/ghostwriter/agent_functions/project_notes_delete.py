from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ProjectNotesDeleteArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="note_id",
                default_value=0,
                description="ID of the project note to delete",
                type=ParameterType.Number
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ProjectNotesDelete(CommandBase):
    cmd = "project_notes_delete"
    needs_admin = False
    help_cmd = "project_notes_delete"
    description = "Delete a note on a project"
    version = 1
    author = "@its_a_feature_"
    argument_class = ProjectNotesDeleteArguments
    supported_ui_features = ["ghostwriter:project_notes_delete"]
    browser_script = BrowserScript(script_name="project_notes_delete", author="@its_a_feature_")
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
            delete_project_note = gql(
                """
                mutation deleteProjectNote($note_id: bigint!){
                    delete_projectNote_by_pk(id: $note_id){
                        id
                    }
                }
                """
            )
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData, query=delete_project_note,
                                                                              variable_values={
                                                                                  "note_id": taskData.args.get_arg("note_id"),
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
