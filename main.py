from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import uuid
import logging


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
db = SQLAlchemy(app)

logging.basicConfig(filename='api.log', level=logging.INFO)


class DocumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    registration_number = db.Column(db.String(36), unique=True, nullable=False)
    relationship = db.Column(db.String())


@app.route('/doc_manage', methods=['POST'])
def create_document():
    try:
        data = request.json

        document_type_name = data['document_type']

        document_type = DocumentType.query.filter_by(name=document_type_name).first()
        type_id = document_type.id
        registration_number = str(uuid.uuid4())
        new_document = Document(
            document_type=type_id,
            title=data['title'],
            content=data['content'],
            registration_number=registration_number,
            relationship=''
        )
        db.session.add(new_document)
        db.session.commit()
        logging.info(f"Создан документ {registration_number}")
        return jsonify({'message': 'Документ создан успешно!'})
    except Exception as e:
        logging.error(f"Ошибка при создании документа: {str(e)}")
        return jsonify({'error': 'Ошибка при создании документа'}, 500)


@app.route('/doc_manage/<string:registration_number>', methods=['DELETE'])
def delete_document(registration_number):
    document = Document.query.filter_by(registration_number=registration_number).first()
    if document:
        try:
            db.session.delete(document)
            db.session.commit()
            logging.info(f"Документ с регистрационным номером {registration_number} был удален")
            return jsonify({'message': 'Документ удален успешно!'})
        except Exception as error:
            logging.error(f"Ошибка при удалении документа: {str(error)}")
            return jsonify({'error': 'Ошибка при удалении документа'}, 515)
    else:
        logging.info(f"Документ с регистрационным номером {registration_number} не найден")
        return jsonify({'message': 'Документ не найден'}, 474)


@app.route('/doc_manage/<string:registration_number>', methods=['PUT'])
def update_document(registration_number):
    document = Document.query.filter_by(registration_number=registration_number).first()
    if document:
        try:
            data = request.json

            document_type_name = data['document_type']
            document_type = DocumentType.query.filter_by(name=document_type_name).first()
            type_id = document_type.id

            document.document_type = type_id
            document.title = data['title']
            document.content = data['content']
            db.session.commit()

            logging.info(f"Документ с регистрационным номером {registration_number} был изменен")
            return jsonify({'message': 'Документ изменен успешно!'})
        except Exception as error:
            logging.error(f"Ошибка при изменении документа {registration_number}: {str(error)}")
            return jsonify({'error': 'Ошибка при изменении документа'}, 525)
    else:
        logging.info(f"Документ с регистрационным номером {registration_number} не найден")
        return jsonify({'message': 'Документ не найден'}, 474)


@app.route('/doc_manage/relationship', methods=['POST'])
def create_document_relationship():
    try:
        data = request.json
        registration_number_doc1 = data['registration_number_doc1']
        registration_number_doc2 = data['registration_number_doc2']

        document1 = Document.query.filter_by(registration_number=registration_number_doc1).first()
        document2 = Document.query.filter_by(registration_number=registration_number_doc2).first()

        rl1 = document1.relationship
        if rl1:
            rl1 = list(set(rl1.split(':') + [registration_number_doc2]))
        else:
            rl1 = [registration_number_doc2]
        rl2 = document2.relationship
        if rl2:
            rl2 = list(set(rl2.split(':') + [registration_number_doc1]))
        else:
            rl2 = [registration_number_doc1]
        document1.relationship = ':'.join(rl1)
        document2.relationship = ':'.join(rl2)
        db.session.commit()

        logging.info(f"Создана связь между документами {registration_number_doc1} и {registration_number_doc2}")
        return jsonify({'message': 'Связь между документами создана успешно!'})
    except Exception as e:
        logging.error(f"Ошибка при создании связи между документами: {str(e)}")
        return jsonify({'error': 'Ошибка при создании связи между документами'}, 544)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
