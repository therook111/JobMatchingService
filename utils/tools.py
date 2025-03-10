cv_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_information",
            "description": "Extracts the relevant information from the user's CV",
            "parameters": {
                "type": "object",
                "properties": {
                    "experience": {
                        "type": "string",
                        "description": "The experience the candidate has. Infer this from the users CV. Must be left blank if the candidate has no experience mentioned.",
                    },
                    "soft_skill": {
                        "type": "string",
                        "description": "The soft skill the candidate has. Infer this from the users CV. Must be left blank if the candidate has no soft skills mentioned.",
                    },
                    "technical_skill": {
                        "type": "string",
                        "description": "The technical skill the candidate has. Infer this from the users CV. Must be left blank if the candidate has no technical skills mentioned.",
                    },
                    "degree": {
                        "type": "string",
                        "description": "The degree and/or certifications the candidate has. Infer this from the users CV. Must be left blank if the candidate has no degree mentioned.",
                    },
                },
                "required": ["experience", "soft_skill", "technical_skill", "degree"],
            },
        }
    }
]

location_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_location",
            "description": "Extracts the district and the province/city from a location string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "district": {
                        "type": "string",
                        "description": """The secondary administrative unit (district-level) of the location string. 
                        Must be left blank if none is mentioned. If it is in Vietnamese, translate it into English.
                        If you do not know, leave it blank.""",
                    },
                    "province": {
                        "type": "string",
                        "description": """The primary administrative unit (province-level) of the location string. 
                        Must be left blank if none is mentioned. If it is in Vietnamese, translate it into English.
                        If you do not know, leave it blank.""",
                    },
                },
                "required": ['district', 'province']
            },
        }
    }
]
