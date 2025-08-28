create_tool_tools = [
    {
        "type": "function",
        "name": "create_tool",
        "description": "Outputs a json schema tool definition that satisfies the functionality desired",
        "parameters": {
            "type": "object",
            "properties": {
               "tool_json_schema": {
                   "type": "string",
                   "description": '''A properly formatted json-schema tool definition.
                   **Example of a tool that computes a horoscope given a sign**
                      {
                          "type": "function",
                          "name": "get_horoscope",
                          "description": "Get today's horoscope for an astrological sign.",
                          "parameters": {
                              "type": "object",
                              "properties": {
                                  "sign": {
                                      "type": "string",
                                      "description": "An astrological sign like Taurus or Aquarius",
                                  },
                              },
                              "required": ["sign"],
                          },
                      },
                   '''
               }
            },
            "required": ["tool_json_schema"],
        },
    },
]