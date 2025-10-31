from flask import Blueprint, request, jsonify, current_app, url_for, render_template, send_file, abort
from ..extensions import db
from ..models import User, Proposal, ProposalItem, Template
from flask_login import login_required, current_user
from uuid import uuid4
from datetime import datetime, timedelta
from ..tasks import generate_pdf_task

proposals_bp = Blueprint('proposals', __name__)

@proposals_bp.route('/', methods=['GET'])
@login_required
def list_proposals():
    proposals = Proposal.query.filter_by(user_id=current_user.id).all()
    result = []
    for p in proposals:
        result.append({
            "id": p.id, "title": p.title, "status": p.status, "total": str(p.total_amount)
        })
    return jsonify(result)

@proposals_bp.route('/', methods=['POST'])
@login_required
def create_proposal():
    data = request.get_json()
    title = data.get('title', 'New Proposal')
    client_name = data.get('client_name')
    client_email = data.get('client_email')
    items = data.get('items', [])

    proposal = Proposal(user_id=current_user.id, title=title, client_name=client_name, client_email=client_email)
    db.session.add(proposal)
    db.session.commit()

    subtotal = 0
    for idx, it in enumerate(items):
        qty = int(it.get('quantity',1))
        up = float(it.get('unit_price',0))
        total = qty * up
        pi = ProposalItem(proposal_id=proposal.id, description=it.get('description',''), quantity=qty, unit_price=up, total_price=total, position=idx)
        db.session.add(pi)
        subtotal += total
    proposal.subtotal = subtotal
    proposal.tax = float(data.get('tax',0))
    proposal.total_amount = subtotal + float(proposal.tax)
    db.session.commit()

    return jsonify({"id":proposal.id}), 201

@proposals_bp.route('/<int:id>/generate_pdf', methods=['POST'])
@login_required
def generate_pdf(id):
    proposal = Proposal.query.get_or_404(id)
    if proposal.user_id != current_user.id:
        abort(403)
    # trigger async task
    task = generate_pdf_task.delay(proposal.id)
    return jsonify({"msg":"pdf-generation-started", "task_id": task.id})

@proposals_bp.route('/<int:id>/share', methods=['POST'])
@login_required
def create_share(id):
    proposal = Proposal.query.get_or_404(id)
    if proposal.user_id != current_user.id:
        abort(403)
    days = int(request.json.get('days', 30))
    proposal.share_uuid = uuid4()
    proposal.share_expiry = datetime.utcnow() + timedelta(days=days)
    db.session.commit()
    share_url = url_for('share.view_shared', share_uuid=str(proposal.share_uuid), _external=True)
    return jsonify({"share_url": share_url})
