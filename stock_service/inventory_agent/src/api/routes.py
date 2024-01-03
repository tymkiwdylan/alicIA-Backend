import json
from flask import Blueprint, request, jsonify
from . import db 
from . import openai_client
from . import functions
from .models import Agent, Conversation

routes = Blueprint('routes', __name__)

def register_functions():
    function_settings = []
    
    for _ , tool_class in functions.items():
        function_settings.append(
            {
                'type': 'function',
                'function': tool_class.settings
                }
            )
    
    return function_settings

def call_function(function_name, **kwargs):
    function = functions.get(function_name, None)
    print(function_name)
    
    if function is None:
        return {'Error': "Function does not exist"}
    
    result = function.execute(**kwargs)
    
    return result['data']


@routes.route('/assistant', methods=['POST'])
def create_assistant():
    data = request.get_json()
    
    company_name = data['company_name']
    user_id = data['user_id']
    
    model = 'gpt-4-1106-preview'
    name = f"{company_name}_inventory_assistant"
    description = f'''This is an inventory Assistant for {company_name}'''
    
    tone = data['tone']
    
    # Update instructions so that they have tools rather than API endpoints
    instructions = f'''
                    **Asistente de Inventario AI con Integración de API de {company_name}**

                    **Descripción del Agente:**  
                    El Asistente de Inventario AI es una herramienta avanzada diseñada para la gestión del inventario de {company_name}. Utiliza la API de Inventario de {company_name}
                    para la recuperación y gestión de datos en tiempo real. Este AI se destaca en proporcionar resúmenes actualizados del inventario, buscar artículos específicos, ajustar precios de los artículos, registrar movimientos de stock, evaluar la valoración del stock y actualizar el inventario. 

                    **Integración de Puntos de Acceso API:**
                    1. **/overview (GET):** Para obtener un resumen del estado actual del inventario.
                    2. **/search (GET):** Para buscar detalladamente artículos en el inventario usando consultas específicas.
                    3. **/price (PUT):** Para actualizar el precio de los artículos, con opciones para ajustar por montos fijos o porcentajes.
                    4. **/movement-log (GET, POST):** Para recuperar y registrar el movimiento de stock, incluyendo cantidad, tipo de movimiento y descripciones.
                    5. **/stock-valuation (GET):** Para obtener una evaluación del stock basada en parámetros especificados.
                    6. /stock (POST): Para actualizar, eliminar o añadir artículos al stock.

                    **Interacción del Usuario y Funcionalidad:**
                    - Proporcionar una interfaz amigable para interactuar con los puntos de acceso de la API.
                    - Ofrecer resúmenes detallados y actualizaciones sobre el estado del inventario.
                    - Habilitar una búsqueda eficiente de artículos y modificaciones de precios.
                    - Mantener registros precisos de movimientos de stock.
                    - Generar informes perspicaces de valoración de stock.

                    **Solicitudes y Reportes Personalizados:**
                    - Responder a consultas personalizadas de usuarios sobre datos de inventario.
                    - Generar y presentar informes personalizados basados en parámetros definidos por el usuario.

                    **Escenarios de Uso:**
                    - Gestión diaria y supervisión del inventario.
                    - Seguimiento específico de artículos y ajustes de precios.
                    - Análisis de movimiento de stock para una mejor gestión de la cadena de suministro.
                    - Evaluaciones financieras y pronósticos basados en valoraciones de stock.

                    **Requisitos Técnicos:**
                    - Asegurar una integración segura y fiable con la API de Inventario de {company_name}.
                    - Adaptarse a cualquier actualización o cambio en la estructura o funcionalidad de la API.

                    **Instrucciones para el Asistente de Inventario AI:**
                    - Utilizar los puntos de acceso de la API para todas las tareas relacionadas con el inventario.
                    - Es importante recordar que item_id se refiere al ID del item en el inventario, y no al SKU del producto
                    - Proporcionar datos y actualizaciones en tiempo real a los usuarios.
                    - Adaptarse a diversos escenarios de gestión de inventario, mostrando versatilidad y precisión.
                    - En caso de buscar un producto y no encontrarlo, usa el inventory overview para encontrar productos similares. A veces el producto simplemente tiene otro nombre.
                    - Nunca mencionar que estás trabajando con una API, en su lugar decir que estás “comunicándote con el Almacén”
                    - Recuerda que eres un especialista, debes proporcionar ideas incluso cuando no se te pida.
                    - Tienes acceso a la herramienta de interpretación de código, asegúrate de usarla para generar gráficos que proporcionen mejores ideas para el usuario.
                    - Si fallan demasiadas tareas, debes decirle al usuario que contacte al soporte técnico en el 362-413-9565.
                    '''
    
    tools = register_functions()
    
    new_assistant = openai_client.beta.assistants.create(
        instructions = instructions,
        name = name,
        model = model,
        description = description,
        tools = tools
    )
    
    if new_assistant == None:
        return 'Error creating assistant', 401
    
    new_agent = Agent(
        id = new_assistant.id,
        user_id = user_id,
        tone = tone,
        company_name = company_name,
        description = description
        )
    
    db.session.add(new_agent)
    db.session.commit()
    
    return 'success', 201



@routes.route('/assistant/<user_id>', methods = ['PUT'])
def update_assistant(user_id):
    
    return 'coming soon', 200

@routes.route('/conversation/<user_id>', methods = ['POST'])
def create_conversation(user_id):
    
    #retrieve agent_id
    agent = Agent.query.filter_by(user_id=user_id).first()
    
    if agent == None:
        return "You haven't set up your agent yet!", 401
    
    # create thread
    
    new_thread = openai_client.beta.threads.create()
    
    new_conversation = Conversation(id = new_thread.id, agent_id=agent.id)
    
    db.session.add(new_conversation)
    db.session.commit()
    
    return 'Conversation created successfully', 201


@routes.route('/conversations', methods = ['GET'])
def get_conversations():
    # Get user_id from params
    # Retrieve all conversations
    # Return as json with 200 status
    user_id = request.args.get('user_id', None)
    
    if user_id == None:
        return 'Missing user_id', 400
    
    agent = Agent.query.filter_by(user_id=int(user_id)).first()
    
    if agent == None:
        return 'user_id invalid', 404
    
    conversations = [conversation.id for conversation in agent.conversations]
    
    return jsonify(data = conversations), 200

@routes.route('/conversation', methods = ['GET'])
def get_conversation_messages():
    # Get thread_id from params
    # Retrieve all messages from thread
    # Return as json with 200 status code
    thread_id = request.args.get('thread_id', None)
    
    if thread_id == None:
        return 'Missing thread_id', 400
    
    messages = openai_client.beta.threads.messages.list(thread_id)
    
    return jsonify(data = messages.data)

@routes.route('/conversation', methods = ['DELETE'])
def delete_conversation():
    # Get Id from params
    # delete from api
    # delete from db
    # return success with status code 204
    thread_id = request.args.get('thread_id', None)
    
    if thread_id == None:
        return 'Missing thread_id', 400
    
    response = openai_client.beta.threads.delete(thread_id)
    
    if response.deleted != True:
        return 'Error deleting thread', 400
    
    conversation = Conversation.query.get(thread_id)
    
    if conversation == None:
        return 'Thread_id invalid', 404
    
    db.session.delete(conversation)
    db.session.commit()
    
    return 'Conversation deleted successfully'
    

@routes.route('/prompt', methods = ['POST'])
def process_prompt():
    # create new message
    # create run
    # Loop until run is not in_progess or qeued
    # Branch to function if neccessary
    # return response
    
    data = request.get_json()
    prompt = data['prompt']
    thread_id = data['thread_id']
    
    agent_id = Conversation.query.get(thread_id).agent_id
    
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user", 
        content=prompt
    )
    
    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=agent_id
    )
    
    while True:
        
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        
        if run.status == 'completed':
            messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            return jsonify(data = text), 201
        
        if run.status == "requires_action":
            tool_call_id = run.required_action.submit_tool_outputs.tool_calls[0]
            function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
            function_arguments = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            
            function_response = call_function(function_name, **function_arguments)
        
            run = openai_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs= [
                    {
                    "tool_call_id": tool_call_id.id,
                    "output": function_response,
                    }
                ],
            )
            
        if run.status == "expired":
            return "Timeout Error", 204
        if run.status == "cancelled":
            return "Request cancelled", 204
        if run.status == "failed":
            return "Request Failed to Complete", 204
        
        
        
    
    
    

    