## Instructions
You will be given a properly formatted json-schema representing a tool definition
for later use. Your task is to accurately translate the tool definition and associated
parameters into a well formatted python function that performs the action specified
by the description and the parameters.

The parameters should be unzipped so there is a parameter in the python method for each parameter in the tool definition.

## Output Format 
Return only the well-formatted python source code with no other output. The generated source should
be compilable with python 3.9. No walrus operators.