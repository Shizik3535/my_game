import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QComboBox, QMessageBox, QStackedWidget, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, Qt
from qt_material import apply_stylesheet

# Контроллер игры: хранит состояние текущего вопроса, раунда, темы, вопросы и игроков
class GameController(QObject):
    update_player_state = pyqtSignal(dict)  # сигнал для оповещения окон об изменениях

    def __init__(self):
        super().__init__()
        self.state = {
            "current_topic": None,
            "current_question": None,
            "current_answer": None,
            "current_value": None,
            "show_answer": False,   # True, если был правильный ответ
            "incorrect": False      # True, если ответ неверный
        }
        # Определяем раунды: первые два обычные, третий – финальный
        self.rounds = {
            "Раунд 1": {
                "Тема 1": [
                    {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                    {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                    {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                    {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                    {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
                ],
                "Тема 2": [
                    {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                    {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                    {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                    {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                    {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
                ]
            },
            "Раунд 2": {
                "Тема 3": [
                    {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                    {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                    {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                    {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                    {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
                ],
                "Тема 4": [
                    {"question": "Вопрос 1", "answer": "Ответ 1", "value": 100, "used": False},
                    {"question": "Вопрос 2", "answer": "Ответ 1", "value": 200, "used": False},
                    {"question": "Вопрос 3", "answer": "Ответ 1", "value": 300, "used": False},
                    {"question": "Вопрос 4", "answer": "Ответ 2", "value": 400, "used": False},
                    {"question": "Вопрос 5", "answer": "Ответ 2", "value": 500, "used": False},
                ]
            },
            "Финальный раунд": {
                "Финальная тема": [
                    {"question": "Финальный вопрос", "answer": "Финальный ответ", "value": 1000, "used": False}
                ]
            }
        }
        self.current_round = "Раунд 1"
        self.players = {}  # ключ – имя игрока, значение – набранные очки

    def add_player(self, name):
        if name and name not in self.players:
            self.players[name] = 0
            self.emit_state()

    def remove_player(self, name):
        if name in self.players:
            del self.players[name]
            self.emit_state()

    def select_question(self, topic, q_index):
        if topic in self.rounds[self.current_round] and len(self.rounds[self.current_round][topic]) > q_index:
            q_data = self.rounds[self.current_round][topic][q_index]
            if q_data.get("used", False):
                return
            self.state["current_topic"] = topic
            self.state["current_question"] = q_data["question"]
            self.state["current_answer"] = q_data["answer"]
            self.state["current_value"] = q_data["value"]
            self.state["show_answer"] = False
            self.state["incorrect"] = False
            self.emit_state()

    def mark_answer(self, player, correct: bool):
        if player in self.players and self.state["current_question"]:
            if correct:
                self.players[player] += self.state.get("current_value", 0)
                self.state["show_answer"] = True
                self.state["incorrect"] = False
                self.emit_state()
                topic = self.state["current_topic"]
                if topic:
                    for q_data in self.rounds[self.current_round][topic]:
                        if q_data["question"] == self.state["current_question"]:
                            q_data["used"] = True
                            break
            else:
                self.state["incorrect"] = True
                self.emit_state()

    def clear_current_question(self):
        self.state = {
            "current_topic": None,
            "current_question": None,
            "current_answer": None,
            "current_value": None,
            "show_answer": False,
            "incorrect": False,
        }
        self.emit_state()

    def is_round_over(self):
        topics = self.rounds[self.current_round]
        return all(all(q.get("used", False) for q in q_list) for q_list in topics.values())

    def advance_round(self):
        if self.current_round == "Раунд 1":
            self.current_round = "Раунд 2"
        elif self.current_round == "Раунд 2":
            self.current_round = "Финальный раунд"
        self.emit_state()

    def previous_round(self):
        if self.current_round == "Финальный раунд":
            self.current_round = "Раунд 2"
        elif self.current_round == "Раунд 2":
            self.current_round = "Раунд 1"
        # Если уже "Раунд 1", возвращение назад не производится.
        self.emit_state()

    def is_game_over(self):
        return self.current_round == "Финальный раунд" and self.is_round_over()

    def emit_state(self):
        data = {
            "state": self.state,
            "rounds": self.rounds,
            "current_round": self.current_round,
            "players": self.players,
            "game_over": self.is_game_over()
        }
        self.update_player_state.emit(data)

# Функция для рекурсивного очищения лэйаута
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clear_layout(item.layout())

# Окно ведущего
class HostWindow(QMainWindow):
    def __init__(self, controller, player_window):
        super().__init__()
        self.controller = controller
        self.player_window = player_window  # для управления слайдами в окне игроков
        self.setWindowTitle("Окно ведущего")
        self.resize(900, 700)
        self.initUI()

    def initUI(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # Отображение названия раунда по центру с отступом сверху 50 пикселей
        self.round_label = QLabel(f"{self.controller.current_round}")
        main_layout.addWidget(self.round_label)

        # Отображение выбранного вопроса (ведущий видит ответ)
        self.current_question_label = QLabel("Нет выбранного вопроса")
        main_layout.addWidget(self.current_question_label)

        # Доска с темами и вопросами
        self.board_layout = QVBoxLayout()
        main_layout.addLayout(self.board_layout)
        self.populate_board()

        # Панель управления: выбор игрока и проверка ответа
        control_layout = QHBoxLayout()
        self.player_select = QComboBox()
        control_layout.addWidget(QLabel("Выберите игрока:"))
        control_layout.addWidget(self.player_select)
        self.btn_correct = QPushButton("Правильный")
        self.btn_incorrect = QPushButton("Неправильный")
        self.btn_correct.clicked.connect(self.mark_correct)
        self.btn_incorrect.clicked.connect(self.mark_incorrect)
        control_layout.addWidget(self.btn_correct)
        control_layout.addWidget(self.btn_incorrect)
        main_layout.addLayout(control_layout)

        # Панель для добавления и удаления игроков
        player_mgmt_layout = QHBoxLayout()
        self.player_input = QLineEdit()
        self.player_input.setPlaceholderText("Имя игрока")
        self.btn_add_player = QPushButton("Добавить игрока")
        self.btn_add_player.clicked.connect(self.add_player)
        self.btn_remove_player = QPushButton("Удалить игрока")
        self.btn_remove_player.clicked.connect(self.remove_player)
        player_mgmt_layout.addWidget(self.player_input)
        player_mgmt_layout.addWidget(self.btn_add_player)
        player_mgmt_layout.addWidget(self.btn_remove_player)
        main_layout.addLayout(player_mgmt_layout)

        # Панель переключения слайдов и перехода между раундами
        slide_layout = QHBoxLayout()
        self.btn_show_welcome = QPushButton("Показать приветствие")
        self.btn_show_board = QPushButton("Показать доску")
        self.btn_show_question = QPushButton("Показать вопрос")
        self.btn_show_results = QPushButton("Показать результаты")
        self.btn_show_credits = QPushButton("Показать титры")
        self.btn_prev_round = QPushButton("Предыдущий раунд")
        self.btn_next_round = QPushButton("Следующий раунд")
        self.btn_show_welcome.clicked.connect(lambda: self.player_window.set_welcome_page())
        self.btn_show_board.clicked.connect(lambda: self.player_window.set_board_page())
        self.btn_show_question.clicked.connect(lambda: self.player_window.set_question_page())
        self.btn_show_results.clicked.connect(lambda: self.player_window.set_results_page())
        self.btn_show_credits.clicked.connect(lambda: self.player_window.set_credits_page())
        self.btn_next_round.clicked.connect(self.advance_round)
        self.btn_prev_round.clicked.connect(self.go_previous_round)
        slide_layout.addWidget(self.btn_show_welcome)
        slide_layout.addWidget(self.btn_show_board)
        slide_layout.addWidget(self.btn_show_question)
        slide_layout.addWidget(self.btn_show_results)
        slide_layout.addWidget(self.btn_show_credits)
        slide_layout.addWidget(self.btn_prev_round)
        slide_layout.addWidget(self.btn_next_round)
        main_layout.addLayout(slide_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.controller.update_player_state.connect(self.update_view)

    def populate_board(self):
        clear_layout(self.board_layout)
        topics = self.controller.rounds[self.controller.current_round]
        for topic, questions in topics.items():
            h_layout = QHBoxLayout()
            topic_label = QLabel(topic)
            h_layout.addWidget(topic_label)
            for i, q in enumerate(questions):
                btn = QPushButton(f"{q['value']}")
                btn.setStyleSheet("QPushButton:disabled { border: 2px solid #ffa3a6; color: #ffa3a6; }")
                btn.clicked.connect(lambda checked, t=topic, idx=i: self.select_question(t, idx))
                btn.setEnabled(not q.get("used", False))
                h_layout.addWidget(btn)
            self.board_layout.addLayout(h_layout)

    def select_question(self, topic, index):
        self.controller.select_question(topic, index)
        st = self.controller.state
        self.current_question_label.setText(
            f"Тема: {st['current_topic']} | Вопрос: {st['current_question']} | Ответ: {st['current_answer']}"
        )
        self.player_window.set_question_page()

    def mark_correct(self):
        player = self.player_select.currentText()
        if not player:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока")
            return
        self.controller.mark_answer(player, True)
        self.player_window.set_question_page()
        QTimer.singleShot(3000, self.finish_question)

    def finish_question(self):
        self.controller.clear_current_question()
        self.player_window.set_board_page()
        self.populate_board()

    def mark_incorrect(self):
        player = self.player_select.currentText()
        if not player:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока")
            return
        self.controller.mark_answer(player, False)
        self.player_window.set_question_page()

    def add_player(self):
        name = self.player_input.text().strip()
        if name:
            self.controller.add_player(name)
            self.player_select.addItem(name)
            self.player_input.clear()
        else:
            QMessageBox.warning(self, "Ошибка", "Введите имя игрока")

    def remove_player(self):
        player = self.player_select.currentText()
        if player:
            self.controller.remove_player(player)
            index = self.player_select.currentIndex()
            self.player_select.removeItem(index)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите игрока для удаления")

    def advance_round(self):
        self.controller.advance_round()
        self.populate_board()
        self.current_question_label.setText("Нет выбранного вопроса")
        self.round_label.setText(f"{self.controller.current_round}")
        self.player_window.set_board_page()

    def go_previous_round(self):
        self.controller.previous_round()
        self.populate_board()
        self.current_question_label.setText("Нет выбранного вопроса")
        self.round_label.setText(f"{self.controller.current_round}")
        self.player_window.set_board_page()

    def update_view(self, data):
        self.populate_board()
        st = data["state"]
        if st["current_question"]:
            self.current_question_label.setText(
                f"Тема: {st['current_topic']} | Вопрос: {st['current_question']} | Ответ: {st['current_answer']}"
            )
        else:
            self.current_question_label.setText("Нет выбранного вопроса")
        self.round_label.setText(f"{data['current_round']}")

# Окно для игроков (только для отображения)
class PlayerWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Окно игроков")
        self.resize(600, 500)
        self.initUI()
        self.controller.update_player_state.connect(self.update_view)
        self.setStyleSheet(
            "QLabel { font-size: 24px; } "
            "QPushButton { font-size: 24px; } "
            "QLineEdit { font-size: 24px; } "
            "QComboBox { font-size: 24px; }"
        )

    def initUI(self):
        self.stack = QStackedWidget()

        # Страница 0: Приветствие
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label = QLabel("Добро пожаловать на игру 'Своя игра - 8 марта'!")
        welcome_layout.addWidget(self.welcome_label)
        self.welcome_page.setLayout(welcome_layout)
        self.stack.addWidget(self.welcome_page)

        # Страница 1: Доска с темами и вопросами (только для чтения)
        self.board_page = QWidget()
        board_layout = QVBoxLayout()
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.round_label = QLabel(f"{self.controller.current_round}")
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.round_label.setStyleSheet("margin-top: 50px;")
        board_layout.addWidget(self.round_label)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.board_container = QWidget()
        self.board_container_layout = QVBoxLayout()
        self.board_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.board_container.setLayout(self.board_container_layout)
        scroll_area.setWidget(self.board_container)
        board_layout.addWidget(scroll_area)
        self.board_page.setLayout(board_layout)
        self.stack.addWidget(self.board_page)

        # Страница 2: Страница вопроса с разделением на 3 зоны
        self.question_page = QWidget()
        q_layout = QVBoxLayout()
        q_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topic_label = QLabel("")
        self.center_question_label = QLabel("")
        self.feedback_label = QLabel("")
        q_layout.addWidget(self.topic_label)
        q_layout.addWidget(self.center_question_label)
        q_layout.addWidget(self.feedback_label)
        self.question_page.setLayout(q_layout)
        self.stack.addWidget(self.question_page)

        # Страница 3: Итоговая страница с результатами
        self.results_page = QWidget()
        r_layout = QVBoxLayout()
        r_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label = QLabel("")
        r_layout.addWidget(self.results_label)
        self.results_page.setLayout(r_layout)
        self.stack.addWidget(self.results_page)

        # Страница 4: Титры
        self.credits_page = QWidget()
        c_layout = QVBoxLayout()
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credits_label = QLabel("")
        c_layout.addWidget(self.credits_label)
        self.credits_page.setLayout(c_layout)
        self.stack.addWidget(self.credits_page)

        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)

    # Методы для переключения страниц
    def set_welcome_page(self):
        self.stack.setCurrentIndex(0)

    def set_board_page(self):
        self.populate_board()
        self.stack.setCurrentIndex(1)

    def set_question_page(self):
        self.update_question_page()
        self.stack.setCurrentIndex(2)

    def set_results_page(self):
        self.update_results_page()
        self.stack.setCurrentIndex(3)

    def set_credits_page(self):
        self.update_credits_page()
        self.stack.setCurrentIndex(4)

    def populate_board(self):
        clear_layout(self.board_container_layout)
        topics = self.controller.rounds[self.controller.current_round]
        for topic, questions in topics.items():
            h_layout = QHBoxLayout()
            topic_label = QLabel(topic)
            h_layout.addWidget(topic_label)
            for q in questions:
                btn = QPushButton(f"{q['value']}")
                btn.setStyleSheet("QPushButton:disabled { border: 2px solid #ffa3a6; color: #ffa3a6; }")
                btn.setEnabled(not q.get("used", False))
                h_layout.addWidget(btn)
            self.board_container_layout.addLayout(h_layout)

    def update_question_page(self):
        state = self.controller.state
        if state["current_question"]:
            self.topic_label.setText(f"{state['current_topic']}")
            self.center_question_label.setText(f"{state['current_question']}")
            if state.get("show_answer", False):
                self.feedback_label.setText(f"{state['current_answer']}")
            elif state.get("incorrect", False):
                self.feedback_label.setText("Неправильный ответ!")
            else:
                self.feedback_label.setText("")
        else:
            self.topic_label.setText("Нет выбранной темы")
            self.center_question_label.setText("Нет выбранного вопроса")
            self.feedback_label.setText("")

    def update_results_page(self):
        scores = self.controller.players
        results_text = "Результаты:\n" + "\n".join(f"{p}: {s}" for p, s in scores.items())
        self.results_label.setText(results_text)

    def update_credits_page(self):
        credits_text = "С 8 марта!\n\nСпасибо за игру!"
        self.credits_label.setText(credits_text)

    def update_view(self, data):
        if self.stack.currentIndex() == 1:
            self.populate_board()
            self.round_label.setText(f"{data['current_round']}")
        elif self.stack.currentIndex() == 2:
            self.update_question_page()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_red.xml')
    controller = GameController()
    # Предзаполнение списка игроков
    default_players = ["Вика", "Алина", "Интизар", "Олеся", "Оля", "Настя", "Арина", "Соня", "Милена", "Марина Юрьевна"]
    for name in default_players:
        controller.add_player(name)
    player_window = PlayerWindow(controller)
    host_window = HostWindow(controller, player_window)
    for name in default_players:
        host_window.player_select.addItem(name)
    host_window.show()
    player_window.show()
    sys.exit(app.exec())
