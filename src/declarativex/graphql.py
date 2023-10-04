from graphql.parser import GraphQLParser  # type: ignore[import]


def extract_variables_from_gql_query(gql_query: str):
    ast = GraphQLParser().parse(gql_query)
    variables = []
    for definition in ast.definitions:
        if definition.variable_definitions:
            for variable_definition in definition.variable_definitions:
                variables.append(variable_definition.name)
    return variables
