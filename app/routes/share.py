from flask import Blueprint, render_template, abort
from ..models import Proposal
from datetime import datetime
from ..extensions import db

share_bp = Blueprint('share', __name__)

@share_bp.route('/<share_uuid>', methods=['GET'])
def view_shared(share_uuid):
    proposal = Proposal.query.filter_by(share_uuid=share_uuid).first_or_404()
    if proposal.share_expiry and proposal.share_expiry < datetime.utcnow():
        abort(410)
    # increment views
    proposal.view_count = (proposal.view_count or 0) + 1
    db.session.commit()

    # render public proposal view (lightweight)
    return render_template('proposal_public_view.html', proposal=proposal)
