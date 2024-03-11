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
                data = data["objective"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "objective":{"plaintext": data[i]["objective"],  "copyIcon": true},
                        "complete": {"plaintext": getCompleteStatus(data[i])},
                        "due": {"plaintext": data[i]["deadline"]},
                        "type": {"plaintext": "objective"},
                        "description": {"plaintext": data[i]["description"]},
                        "status": {"plaintext": data[i]["objectiveStatus"]["objectiveStatus"]},
                        "priority": {"plaintext": data[i]["objectivePriority"]["priority"], "cellStyle": getObjectiveColor(data[i]["objectivePriority"]["priority"])},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Objective Data"
                                    },
                                    {
                                        "name": "Delete Objective",
                                        "startIcon": "delete",
                                        "startIconColor": "red",
                                        "type": "task",
                                        "parameters": {"id": data[i]["id"]},
                                        "ui_feature": "ghostwriter:objectives_delete",
                                        "getConfirmation": true
                                    },
                                    {
                                        "name": "Update Objective",
                                        "type": 'task',
                                        "ui_feature": "ghostwriter:objectives_update",
                                        "openDialog": true,
                                        "parameters": {
                                            id: data[i]["id"],
                                            complete: data[i]["complete"],
                                            description: data[i]["description"],
                                            objective: data[i]["objective"],
                                            status: data[i]["objectiveStatus"]["objectiveStatus"],
                                            priority: data[i]["objectivePriority"]["priority"]
                                        }
                                    },
                                    {
                                        "name": "Create Subtask",
                                        "type": 'task',
                                        "ui_feature": "ghostwriter:objectives_create_subtask",
                                        "openDialog": true,
                                        "parameters": {
                                            parentId: data[i]["id"],
                                        }
                                    }
                                ]
                            }},
                    });
                    for(let j = 0; j < data[i]["objectiveSubTasks"].length; j++){
                        output_table.push({
                            "objective":{"plaintext": data[i]["objectiveSubTasks"][j]["task"],  "copyIcon": true},
                            "complete": {"plaintext": getCompleteStatus(data[i]["objectiveSubTasks"][j])},
                            "due": {"plaintext": data[i]["objectiveSubTasks"][j]["deadline"]},
                            "description": {"plaintext": ""},
                            "type": {"plaintext": "subtask"},
                            "status": {"plaintext": data[i]["objectiveSubTasks"][j]["objectiveStatus"]["objectiveStatus"]},
                            "priority": {"plaintext": data[i]["objectivePriority"]["priority"], "cellStyle": getObjectiveColor(data[i]["objectivePriority"]["priority"])},
                            "actions": {"button": {
                                    "name": "Actions",
                                    "type": "menu",
                                    "value": [
                                        {
                                            "name": "View All Data",
                                            "type": "dictionary",
                                            "value": data[i]["objectiveSubTasks"][j],
                                            "leftColumnTitle": "Key",
                                            "rightColumnTitle": "Value",
                                            "title": "Viewing Objective Data"
                                        },
                                        {
                                            "name": "Delete Objective",
                                            "startIcon": "delete",
                                            "startIconColor": "red",
                                            "type": "task",
                                            "parameters": {"id": data[i]["objectiveSubTasks"][j]["id"]},
                                            "ui_feature": "ghostwriter:objectives_delete_subtask",
                                            "getConfirmation": true
                                        },
                                        {
                                            "name": "Update Objective",
                                            "type": 'task',
                                            "ui_feature": "ghostwriter:objectives_update_subtask",
                                            "openDialog": true,
                                            "parameters": {
                                                id: data[i]["objectiveSubTasks"][j]["id"],
                                                complete: data[i]["objectiveSubTasks"][j]["complete"],
                                                task: data[i]["objectiveSubTasks"][j]["task"],
                                                status: data[i]["objectiveSubTasks"][j]["objectiveStatus"]["objectiveStatus"]
                                            }
                                        }
                                    ]
                                }},
                        })
                    }
                }
                output_table.push({
                    "objective":{"plaintext": ""},
                    "complete": {"plaintext": ""},
                    "due": {"plaintext": ""},
                    "description": {"plaintext": ""},
                    "status": {"plaintext": ""},
                    "type": {"plaintext": ""},
                    "priority": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "Create Objective",
                        "type": 'task',
                            "startIcon": "upload",
                        "ui_feature": "ghostwriter:objectives_create",
                        "openDialog": true,
                        "parameters": {}
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "type", "type": "string", "width": 70},
                                {"plaintext": "objective", "type": "string", "fillWidth": true},
                                {"plaintext": "complete", "type": "string", "width": 100},
                                {"plaintext": "due", "type": "string", "width": 100},
                                {"plaintext": "description", "type": "string", "fillWidth": true},
                                {"plaintext": "status", "type": "string", "width": 70},
                                {"plaintext": "priority", "type": "string", "width": 70},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Project Objectives"
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