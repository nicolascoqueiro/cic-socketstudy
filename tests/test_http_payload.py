import unittest
import urllib.request
import json

class TestHTTPPayload(unittest.TestCase):
    def setUp(self):
        self.url_msg = "http://127.0.0.1:5000/messages"
        self.url_reg = "http://127.0.0.1:5000/register"
        
        dados_user = json.dumps({"username": "nicolas", "password": "123"}).encode('utf-8')
        req = urllib.request.Request(self.url_reg, data=dados_user, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req) as res:
                res.read()
        except urllib.error.HTTPError as e:
            e.read()
        except Exception:
            pass

    def test_payload_valido(self):
        """Testa o envio de uma mensagem com tamanho menor que 500 caracteres."""
        dados = json.dumps({"username": "nicolas", "content": "Mensagem curta válida."}).encode('utf-8')
        req = urllib.request.Request(self.url_msg, data=dados, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req) as res:
                self.assertEqual(res.getcode(), 200)
                res.read()
        except Exception as e:
            self.fail(f"Deveria aceitar payload válido. Erro: {e}")

    def test_payload_excedido(self):
        """Testa o bloqueio de uma mensagem com mais de 500 caracteres."""
        texto_gigante = "A" * 501
        dados = json.dumps({"username": "nicolas", "content": texto_gigante}).encode('utf-8')
        req = urllib.request.Request(self.url_msg, data=dados, headers={'Content-Type': 'application/json'}, method='POST')
        
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        
        self.assertEqual(cm.exception.code, 400)
        cm.exception.read()

if __name__ == '__main__':
    unittest.main()