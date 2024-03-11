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
                data = data["finding"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "title":{"plaintext": data[i]["title"],  "copyIcon": true},
                        "severity": {"plaintext": data[i]["severity"]["severity"] + "(" + data[i]["cvssScore"] + ")",
                            "cellStyle": {
                                color: `#${data[i]["severity"]["color"]}`,
                                fontWeight: "bold",
                            }},
                        "type": {"plaintext": data[i]["type"]["findingType"]},
                        "description": {"plaintext":data[i]["description"],  "copyIcon": true},
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
                                        "name": "Use Finding",
                                        "type": 'task',
                                        "ui_feature": "ghostwriter:findings_attach",
                                        "openDialog": true,
                                        "parameters": {
                                            findingId: data[i]["id"],

                                        }
                                    },
                                ]
                            }},
                    });
                }
                output_table.push({
                    "title":{"plaintext": ""},
                    "severity": {"plaintext": ""},
                    "cvss": {"plaintext": ""},
                    "type": {"plaintext": ""},
                    "description": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "Create Blank Finding",
                        "type": 'task',
                        "startIcon": "upload",
                        "ui_feature": "ghostwriter:findings_create_blank",
                        "openDialog": true,
                        "parameters": {}
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "title", "type": "string", "fillWidth": true},
                                {"plaintext": "severity", "type": "string", width: 70},
                                {"plaintext": "type", "type": "string", width: 50},
                                {"plaintext": "description", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Findings"
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