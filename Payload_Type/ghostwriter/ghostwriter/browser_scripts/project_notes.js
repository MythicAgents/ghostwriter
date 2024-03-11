function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            try{
                let data = JSON.parse(responses[0]);
                data = data["projectNote"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "user":{"plaintext": data[i]["user"]["username"]},
                        "note": {"plaintext": data[i]["note"]},
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
                                        "title": "Viewing Project Note Data"
                                    },
                                    {
                                        "name": "Edit",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:project_notes_update",
                                        "openDialog": true,
                                        "parameters": {
                                            note_id: data[i]["id"],
                                            note: data[i]["note"]
                                        }
                                    },
                                    {
                                        "name": "Delete",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:project_notes_delete",
                                        "getConfirmation": true,
                                        "startIcon": "delete",
                                        "parameters": {
                                            note_id: data[i]["id"],
                                        }
                                    },
                                ]
                            }},
                    });
                }
                output_table.push({
                    "user":{"plaintext": ""},
                    "note": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "Create New Blank",
                        "type": 'task',
                        "startIcon": "upload",
                        "ui_feature": "ghostwriter:project_notes_create",
                        "openDialog": true,
                        "parameters": {
                        }
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "user", "type": "string", width: 100},
                                {"plaintext": "note", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Project Notes"
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