function(task, responses){
    function getReportTitle(data) {
        if(data?.finding){
            return data?.finding?.title;
        }
        return data?.report?.title;
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
                data = data["evidence"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "name": {"plaintext": data[i]["friendlyName"]},
                        "description": {"plaintext":  data[i]["description"]},
                        "caption": {"plaintext": data[i]["caption"]},
                        "document": {"plaintext": data[i]["document"]},
                        "finding/report": {"plaintext": getReportTitle(data[i])},
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
                                        "title": "Viewing Evidence Data"
                                    },
                                    {
                                        "name": "Update",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:evidence_update",
                                        "openDialog": true,
                                        "parameters": {
                                            evidence_id: data[i]["id"],
                                            description: data[i]["description"],
                                            caption: data[i]["caption"],
                                            friendlyName: data[i]["friendlyName"]
                                        }
                                    },
                                    {
                                        "name": "Delete",
                                        "type": "task",
                                        "ui_feature": "ghostwriter:evidence_delete",
                                        "getConfirmation": true,
                                        "startIcon": "delete",
                                        "parameters": {
                                            evidence_id: data[i]["id"],
                                        }
                                    },
                                ]
                            }},
                    });
                }
                output_table.push({
                    "name": {"plaintext": ""},
                    "description": {"plaintext": ""},
                    "caption": {"plaintext": ""},
                    "document": {"plaintext": ""},
                    "finding/report": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "New Report Evidence",
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
                                {"plaintext": "name", "type": "string", width: 100},
                                {"plaintext": "description", "type": "string", "fillWidth": true},
                                {"plaintext": "caption", "type": "string", "fillWidth": true},
                                {"plaintext": "document", "type": "string", "width": 100},
                                {"plaintext": "finding/report", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Reported Evidence"
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