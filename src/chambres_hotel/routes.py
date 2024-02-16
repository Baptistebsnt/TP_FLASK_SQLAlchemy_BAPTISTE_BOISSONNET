from flask import Blueprint
from .database import db
from .models import Chambre, Reservation
from flask import request
from flask import jsonify
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/api/chambres/disponibles', methods=['GET'])
def getChambresDisponibles():
    data = request.get_json()
    
    date_arrivee = datetime.strptime(data['date_arrivee'], '%Y-%m-%d')
    date_depart = datetime.strptime(data['date_depart'], '%Y-%m-%d')

    if not all([date_arrivee, date_depart]):
        return jsonify({"success": False, "message": "Les dates de réservation sont obligatoires."}), 400
    
    # Requête pour obtenir les réservations existantes qui chevauchent les dates spécifiées
    reservations_existantes = Reservation.query.filter(
        Reservation.date_depart > date_arrivee,
        Reservation.date_arrivee < date_depart
    ).all()
    
    # Liste pour stocker les chambres disponibles
    chambres_disponibles = []
    
    # Vérifier la disponibilité de chaque chambre
    for chambre in Chambre.query.all():
        est_disponible = not any(
            reservation.id_chambre == chambre.id
            for reservation in reservations_existantes
        )
        if est_disponible:
            chambres_disponibles.append({
                "id": chambre.id,
                "numero": chambre.numero,
                "type": chambre.type,
                "prix": chambre.prix
            })
    
    return jsonify(chambres_disponibles)


@main.route("/api/reservations", methods=['POST'])
def createReservation():
    data = request.get_json()
    
    id_client = data.get('id_client')
    id_chambre = data.get('id_chambre')
    date_arrivee = data.get('date_arrivee')
    date_depart = data.get('date_depart')
    
    if not all([id_client, id_chambre, date_arrivee, date_depart]):
        return jsonify({"success": False, "message": "Tous les champs doivent être remplis."}), 400
    
    # Vérifiez si la chambre est disponible pour les dates spécifiées
    chambre = Chambre.query.get(id_chambre)
    if not chambre:
        return jsonify({"success": False, "message": "La chambre spécifiée n'existe pas."}), 404
    
    reservations_existantes = Reservation.query.filter(
        Reservation.id_chambre == id_chambre,
        Reservation.date_depart > date_arrivee,
        Reservation.date_arrivee < date_depart
    ).all()
    
    if reservations_existantes:
        return jsonify({"success": False, "message": "La chambre spécifiée n'est pas disponible pour les dates sélectionnées."}), 400
    
    nouvelle_reservation = Reservation(id_client=id_client, id_chambre=id_chambre, date_arrivee=date_arrivee, date_depart=date_depart)
    db.session.add(nouvelle_reservation)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Réservation créée avec succès."}), 201

@main.route("/api/reservations/<int:id>", methods=['DELETE'])
def deleteReservation(id):
    reservation = Reservation.query.get(id)
    
    if reservation is None:
        return "Réservation non trouvée", 404
    
    db.session.delete(reservation)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Réservation annulée avec succès."}), 200

@main.route("/api/chambres", methods=['POST'])
def createChambre():
    data = request.json
    
    numero = data.get('numero')
    chambre_type = data.get('type')
    prix = data.get('prix')
    
    if not all([numero, chambre_type, prix]):
        return jsonify({"success": False, "message": "Tous les champs doivent être remplis."}), 400
    
    nouvelle_chambre = Chambre(numero=numero, type=chambre_type, prix=prix)
    
    db.session.add(nouvelle_chambre)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Chambre ajoutée avec succès."}), 201


@main.route("/api/chambres/<int:id>", methods=['PUT'])
def updateChambre(id):
    chambre = Chambre.query.get(id)
    
    data = request.json
    chambre.numero = data.get('numero', chambre.numero)
    chambre.type = data.get('type', chambre.type)
    chambre.prix = data.get('prix', chambre.prix)
    
    db.session.commit()
    return jsonify({"success": True, "message": "Chambre mise à jour avec succès."}), 200

@main.route("/api/chambres/<int:id>", methods=['DELETE'])
def deleteChambre(id):
    chambre = Chambre.query.get(id)
    
    if chambre is None:
        return "Chambre non trouvée", 404
    
    db.session.delete(chambre)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Chambre supprimée avec succès."}), 200