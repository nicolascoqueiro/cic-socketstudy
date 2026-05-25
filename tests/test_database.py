import unittest
import sqlite3
import os
from servidor.database.db_manager import DBManager

class TestChatDatabase(unittest.TestCase):
    def setUp(self):
        """Configura um gestor de banco de dados apontado para um arquivo de testes."""
        self.db_test_path = os.path.join(os.path.dirname(__file__), 'test_chat.db')
        
        # Sobrescreve o caminho do banco no DBManager para isolar os testes
        self.db = DBManager()
        self.db.db_path = self.db_test_path
        self.db._init_db()

    def tearDown(self):
        """Remove o arquivo de banco de dados temporário após cada teste."""
        if os.path.exists(self.db_test_path):
            os.remove(self.db_test_path)

    def test_user_uniqueness(self):
        """Valida que a restrição UNIQUE impede utilizadores duplicados."""
        # Primeiro registo deve ter sucesso
        sucesso1 = self.db.register_user("nicolas_teste", "senha123")
        self.assertTrue(sucesso1)

        # Segundo registo com o mesmo nome deve falhar devido à restrição UNIQUE
        sucesso2 = self.db.register_user("nicolas_teste", "outrasenha")
        self.assertFalse(sucesso2)

    def test_foreign_key_cascade(self):
        """Valida que ON DELETE CASCADE remove mensagens ao eliminar o utilizador."""
        # 1. Cria o utilizador e obtém o ID
        self.db.register_user("user_deletar", "123")
        
        with sqlite3.connect(self.db_test_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE username = 'user_deletar'")
            user_id = cursor.fetchone()[0]

            # 2. Insere uma mensagem vinculada a este utilizador
            cursor.execute("INSERT INTO mensagens (sender_id, content) VALUES (?, ?)", (user_id, "Mensagem de teste"))
            conn.commit()

            # Verifica que a mensagem foi guardada
            cursor.execute("SELECT COUNT(*) FROM mensagens WHERE sender_id = ?", (user_id,))
            self.assertEqual(cursor.fetchone()[0], 1)

            # 3. Elimina o utilizador (Simulando uma remoção administrativa)
            conn.execute("PRAGMA foreign_keys = ON;") # Garante ativação no socket do teste
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            conn.commit()

            # 4. Assegura que a mensagem foi apagada automaticamente (CASCADE)
            cursor.execute("SELECT COUNT(*) FROM mensagens WHERE sender_id = ?", (user_id,))
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_system_logging(self):
        """Valida a inserção e integridade do histórico na tabela de logs."""
        self.db.log_event("ALERTA_SEGURANCA", "Mensagem de 600 bytes intercetada.")
        
        with sqlite3.connect(self.db_test_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT log_type, description FROM logs_sistema WHERE log_type = 'ALERTA_SEGURANCA'")
            log = cursor.fetchone()
            
            self.assertIsNotNone(log)
            self.assertEqual(log[0], "ALERTA_SEGURANCA")
            self.assertEqual(log[1], "Mensagem de 600 bytes intercetada.")

if __name__ == '__main__':
    unittest.main()