function(task, responses){
    function getCompleteStatus(entry){
        if(entry["complete"]){
            return "Ready";
        }
        return "Needs Editing";
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
                data = data["reportedFinding"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "title":{"plaintext": data[i]["title"],  "copyIcon": true},
                        "severity": {"plaintext": data[i]["severity"]["severity"] + "(" + data[i]["cvssScore"] + ")",
                            "cellStyle": {
                                color: `#${data[i]["severity"]["color"]}`,
                                fontWeight: "bold",
                            }},
                        "status": {"plaintext": getCompleteStatus(data[i])},
                        "reviewer": {"plaintext": data[i]["assignedTo"]?.["username"] || "TBD"},
                        "type": {"plaintext": data[i]["findingType"]["findingType"]},
                        "report": {"plaintext": data[i]["report"]["title"]},
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
                                        "title": "Viewing Findings Data"
                                    },
                                    {
                                        "name": "Update",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:findings_update",
                                        "openDialog": true,
                                        "parameters": {
                                            finding_id: data[i]["id"],
                                            "title": data[i]["title"],
                                            "description": data[i]["description"],
                                            "cvssScore": data[i]["cvssScore"],
                                            "complete": data[i]["complete"]
                                        }
                                    },
                                    {
                                        "name": "Add Evidence",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:evidence_create",
                                        "openDialog": true,
                                        "parameters": {
                                            finding_id: data[i]["id"],
                                        }
                                    },
                                    {
                                        "name": "Delete",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:findings_delete",
                                        "getConfirmation": true,
                                        "startIcon": "delete",
                                        "parameters": {
                                            finding_id: data[i]["id"],
                                        }
                                    },
                                ]
                            }},
                    });
                }
                output_table.push({
                    "title":{"plaintext": ""},
                    "severity": {"plaintext": ""},
                    "status": {"plaintext": ""},
                    "reviewer": {"plaintext": ""},
                    "type": {"plaintext": ""},
                    "report": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "Create Finding",
                        "type": 'task',
                        "startIcon": "upload",
                        "ui_feature": "ghostwriter:findings_create_blank",
                        "openDialog": true,
                        "parameters": {

                        }
                        }},
                });
                output_table.push({
                    "title":{"plaintext": ""},
                    "severity": {"plaintext": ""},
                    "status": {"plaintext": ""},
                    "reviewer": {"plaintext": ""},
                    "type": {"plaintext": ""},
                    "report": {"plaintext": ""},
                    "actions": {"button": {
                            "name": "Create Evidence",
                            "type": 'task',
                            "startIcon": "upload",
                            "ui_feature": "ghostwriter:evidence_create_blank",
                            "openDialog": true,
                            "parameters": {

                            }
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "title", "type": "string", "fillWidth": true},
                                {"plaintext": "severity", "type": "string", width: 100},
                                {"plaintext": "status", "type": "string", "width": 100},
                                {"plaintext": "reviewer", "type": "string", "fillWidth": true},
                                {"plaintext": "type", "type": "string", "width": 70},
                                {"plaintext": "report", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Reported Findings"
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