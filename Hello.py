import streamlit as st
import openai
import time
import uuid

# Seleção do modelo preferido
MODEL = "gpt-4-1106-preview"

# Verifica se há uma sessão em andamento
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Verifica o estado da execução do assistente
if "run" not in st.session_state:
    st.session_state.run = {"status": None}

# Verifica as mensagens do assistente
if "messages" not in st.session_state:
    st.session_state.messages = []

# Contador de erros de retry
if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

# Configuração da página
st.set_page_config(page_title="Learn Wardley Mapping")

# Sidebar
st.sidebar.title("Learn Wardley Mapping")
st.sidebar.divider()
st.sidebar.markdown("Desenvolvido por [Mark Craddock](https://twitter.com/mcraddock)", unsafe_allow_html=True)
st.sidebar.markdown("Versão Atual: 0.0.3")
st.sidebar.markdown("Usando a API gpt-4-1106-preview")
st.sidebar.markdown(st.session_state.session_id)
st.sidebar.divider()

# Verifica se há um assistente em andamento
if "assistant" not in st.session_state:
      openai.api_key = st.secrets["OPENAI_API_KEY"]
    # Substitua 'ID_DA_SUA_ASSISTENTE' pelo ID real da sua assistente existente
    assistent_id = st.secrets["ID_DA_SUA_ASSISTENTE"]

    # Carrega a assistente existente
    st.session_state.assistant = openai.ChatCompletion.retrieve(id=assistent_id)

    # Cria um novo thread para esta sessão
    st.session_state.thread = None  # Alterado para não criar um novo thread aqui, será criado durante a interação do usuário

# Se a execução estiver concluída, exibe as mensagens
elif st.session_state.run.get('status') == "completed":
    # Recupera a lista de mensagens
    st.session_state.messages = openai.ChatCompletion.retrieve(id=st.session_state.run['id']).get('data', [])

    # Exibe as mensagens
    for message in reversed(st.session_state.messages):
        if message['role'] in ["user", "assistant"]:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

# Se houver uma prompt do usuário, adiciona à thread e executa o assistente
if prompt := st.chat_input("How can I help you?"):
    with st.chat_message('user'):
        st.write(prompt)

    # Adiciona a mensagem à thread
    if st.session_state.thread is None:
        st.session_state.thread = openai.Thread.create()

    openai.ChatCompletion.append(
        id=st.session_state.assistant['id'],
        messages=[{"role": "user", "content": prompt}],
        thread_id=st.session_state.thread['id']
    )

    # Executa o assistente
    st.session_state.run = openai.Run.create(
        model=MODEL,
        thread_id=st.session_state.thread['id']
    )

    # Adiciona um pequeno atraso antes de verificar o status da execução
    time.sleep(1)
    st.rerun()

