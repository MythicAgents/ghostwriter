function(task, responses){
    function getExtraFieldsArray(data) {
        let extraFields = [];
        for(const[key, val] of Object.entries(data["extraFields"])){
            extraFields.push(`${key}:${val}`);
        }
        return extraFields;
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
                data = data["oplogEntry"];
                let output_table = [];
                let oplogEntryValue = 0;
                let extraFields = [];
                for(let i = 0; i < data.length; i++){
                    if(i === 0){
                        oplogEntryValue = data[i]["oplog"];
                        for(const[key, val] of Object.entries(data[i]["extraFields"])){
                            extraFields.push(`${key}:${val}`);
                        }
                    }
                    output_table.push({
                        "command":{"plaintext": data[i]["command"],  "copyIcon": true},
                        "comments": {"plaintext": data[i]["comments"]},
                        "description": {"plaintext": data[i]["description"]},
                        "ips": {"plaintext":data[i]["sourceIp"] + "->" + data[i]["destIp"],  "copyIcon": true},
                        "tool": {"plaintext": data[i]["tool"]},
                        "userContext": {"plaintext": data[i]["userContext"]},
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
                                        "name": "Edit Oplog Entry",
                                        "type": 'task',
                                        "startIcon": "list",
                                        "ui_feature": "ghostwriter:oplog_update",
                                        "openDialog": true,
                                        "parameters": {
                                            "oplogEntry_id": data[i]["id"],
                                            "extraFields": getExtraFieldsArray(data[i]),
                                            "command": data[i]["command"],
                                            "comments": data[i]["comments"],
                                            "description": data[i]["description"],
                                            "destIp": data[i]["destIp"],
                                            "sourceIp": data[i]["sourceIp"],
                                            "tool": data[i]["tool"],
                                            "userContext": data[i]["userContext"]
                                        }
                                    },
                                    {
                                        "name": "Create Oplog Entry",
                                        "type": 'task',
                                        "startIcon": "upload",
                                        "ui_feature": "ghostwriter:oplog_create",
                                        "openDialog": true,
                                        "parameters": {
                                            "oplog": data[i]["oplog"],
                                            "extraFields": getExtraFieldsArray(data[i])
                                        }
                                    }
                                ]
                            }},
                    });
                }
                output_table.push({
                    "command":{"plaintext": ""},
                    "comments": {"plaintext": ""},
                    "description": {"plaintext": ""},
                    "ips": {"plaintext": ""},
                    "tool": {"plaintext": ""},
                    "userContext": {"plaintext": ""},
                    "actions": {"button": {
                        "name": "Create Oplog Entry",
                        "type": 'task',
                        "startIcon": "upload",
                        "ui_feature": "ghostwriter:oplog_create",
                        "openDialog": true,
                        "parameters": {
                            "oplog": oplogEntryValue,
                            "extraFields": extraFields
                        }
                        }},
                });
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "command", "type": "string", "fillWidth": true},
                                {"plaintext": "comments", "type": "string", width: 70},
                                {"plaintext": "description", "type": "string", width: 50},
                                {"plaintext": "ips", "type": "string", "fillWidth": true},
                                {"plaintext": "tool", "type": "string", width: 50},
                                {"plaintext": "userContext", "type": "string", width: 100},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Oplog Search"
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