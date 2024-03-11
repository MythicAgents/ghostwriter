function(task, responses){
    function getCompleteStatus(entry){
        if(entry["complete"]){
            if(entry["markedComplete"] !== "" && entry["markedComplete"]){
                return entry["markedComplete"];
            }
            return "True";
        }
        return "False";
    }
    function getObjectiveColor(priority){
        switch (priority) {
            case "Primary":
                return {"backgroundColor": "rgb(251, 139, 138)"}
            case "Secondary":
                return {"backgroundColor": "rgb(242, 183, 145)"}
            default:
                return {"backgroundColor": "rgb(177, 213, 154)"}
        }
    }
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            try{
                let data = JSON.parse(responses[0]);
                data = data["update_objectiveSubTask_by_pk"];
                let output_table = [];
                output_table.push({
                    "objective":{"plaintext": data["task"],  "copyIcon": true},
                    "complete": {"plaintext": getCompleteStatus(data)},
                    "due": {"plaintext": data["deadline"]},
                    "description": {"plaintext": ""},
                    "priority": {"plaintext": ""},
                    "status": {"plaintext": data["objectiveStatus"]["objectiveStatus"]},
                    "actions": {"button": {
                            "name": "Actions",
                            "type": "menu",
                            "value": [
                                {
                                    "name": "View All Data",
                                    "type": "dictionary",
                                    "value": data,
                                    "leftColumnTitle": "Key",
                                    "rightColumnTitle": "Value",
                                    "title": "Viewing Objective Data"
                                },
                                {
                                    "name": "Delete Objective",
                                    "startIcon": "delete",
                                    "startIconColor": "red",
                                    "type": "task",
                                    "parameters": {"id": data["id"]},
                                    "ui_feature": "ghostwriter:objectives_delete_subtask",
                                    "getConfirmation": true
                                },
                                {
                                    "name": "Update Objective",
                                    "type": 'task',
                                    "ui_feature": "ghostwriter:objectives_update_subtask",
                                    "openDialog": true,
                                    "parameters": {
                                        id: data["id"],
                                        complete: data["complete"],
                                        task: data["task"],
                                        status: data["objectiveStatus"]
                                    }
                                }
                            ]
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "objective", "type": "string", "fillWidth": true},
                                {"plaintext": "complete", "type": "string", "width": 100},
                                {"plaintext": "due", "type": "string", "width": 100},
                                {"plaintext": "description", "type": "string", "fillWidth": true},
                                {"plaintext": "status", "type": "string", "width": 70},
                                {"plaintext": "priority", "type": "string", "width": 70},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Updated Objective Subtask"
                        }
                    ]
                }
            }catch(error){
                console.log(error);
                const combined = responses.reduce( (prev, cur) => {
                    return prev + cur;
                }, "");
                return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}