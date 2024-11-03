from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def hello_world(self):
        # Prueba de carga para el endpoint "/"
        self.client.get("/")

    @task(2)
    def ping(self):
        # Prueba de carga para el endpoint "/ping"
        self.client.get("/ping")

    @task(5)
    def consultar_modelo(self):
        # Prueba de carga para el endpoint "/consultar-modelo-gpt" con datos válidos
        payload = {
            "mensaje": "¿Es seguro este mensaje que me envió mi banco?"
        }
        self.client.post("/consultar-modelo-gpt", json=payload)

    @task(1)
    def consultar_modelo_mensaje_faltante(self):
        # Prueba de carga para el endpoint "/consultar-modelo-gpt" sin el campo 'mensaje'
        self.client.post("/consultar-modelo-gpt", json={})

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
