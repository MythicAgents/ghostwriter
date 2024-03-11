from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ProjectNotesCreateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
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


class ProjectNotesCreate(CommandBase):
    cmd = "project_notes_create"
    needs_admin = False
    help_cmd = "project_notes_create -note this is my note"
    description = "Create a note on a project"
    version = 1
    author = "@its_a_feature_"
    argument_class = ProjectNotesCreateArguments
    supported_ui_features = ["ghostwriter:project_notes_create"]
    browser_script = BrowserScript(script_name="project_notes_create", author="@its_a_feature_")
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
                mutation updateProjectNote($project_id: bigint!, $note: String!){
                    insert_projectNote_one(object: {note: $note, projectId: $project_id}) {
                        id
                        note
                    }
                }
                """
            )
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData,
                                                                              query=edit_project_note,
                                                                              variable_values={
                                                                                  "project_id": GhostwriterAPI.get_project_id(
                                                                                      taskData=taskData),
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
