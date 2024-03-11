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
                data = data["report"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "title":{"plaintext": data[i]["title"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "Add Blank Finding",
                                        "type": 'task',
                                        "ui_feature": "ghostwriter:findings_create_blank",
                                        "openDialog": true,
                                        "parameters": {
                                            report: data[i]["title"],
                                        }
                                    },
                                    {
                                        "name": "Add Report Evidence",
                                        "type": 'task',
                                        "ui_feature": "ghostwriter:evidence_create_blank",
                                        "openDialog": true,
                                        "parameters": {
                                            report: data[i]["title"],
                                        }
                                    },
                                ]
                            }},
                    });
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "title", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Current Reports"
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