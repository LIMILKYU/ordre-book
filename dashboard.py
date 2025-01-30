# notification/dashboard.py

import logging
from flask import Flask, jsonify, render_template_string

class Dashboard:
    """
    간단한 Flask 웹 서버로 실시간 데이터 시각화 (스켈레톤)
    """

    def __init__(self, port=5000, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.port = port
        self.app = Flask(__name__)
        self._data_store = {
            "last_price": None,
            "order_book": [],
            "positions": []
        }

        # 라우트 설정
        @self.app.route("/")
        def index():
            return self.render_index()

        @self.app.route("/data")
        def data():
            return jsonify(self._data_store)

    def render_index(self):
        """
        간단한 HTML 템플릿, 실무에서는 별도 .html 파일을 사용 가능
        """
        template = """
        <html>
        <head>
            <title>Real-time Dashboard</title>
        </head>
        <body>
            <h1>My Trading Dashboard</h1>
            <p>Last Price: {{ last_price }}</p>
            <h2>Order Book</h2>
            <ul>
            {% for bidask in order_book %}
                <li>{{ bidask }}</li>
            {% endfor %}
            </ul>
            <h2>Positions</h2>
            <ul>
            {% for pos in positions %}
                <li>{{ pos }}</li>
            {% endfor %}
            </ul>
        </body>
        </html>
        """
        return render_template_string(
            template,
            last_price=self._data_store["last_price"],
            order_book=self._data_store["order_book"],
            positions=self._data_store["positions"],
        )

    def start(self):
        """
        Flask 앱 실행 (blocking)
        """
        self.logger.info(f"Starting dashboard on port {self.port}...")
        self.app.run(host="0.0.0.0", port=self.port, debug=False)

    def update_data(self, last_price=None, order_book=None, positions=None):
        """
        외부에서 새로운 데이터를 받아서 _data_store를 업데이트
        """
        if last_price is not None:
            self._data_store["last_price"] = last_price
        if order_book is not None:
            self._data_store["order_book"] = order_book
        if positions is not None:
            self._data_store["positions"] = positions
