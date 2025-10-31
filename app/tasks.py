import os
import pdfkit
from celery import Celery
from flask import current_app, render_template, url_for
from .models import Proposal, ProposalItem
from .extensions import db
import boto3

celery = Celery(__name__, broker=os.environ.get("REDIS_URL"), backend=os.environ.get("REDIS_URL"))

@celery.task(bind=True)
def generate_pdf_task(self, proposal_id):
    # needs app context to query DB and render templates
    from app import create_app
    app = create_app()
    with app.app_context():
        proposal = Proposal.query.get(proposal_id)
        if not proposal:
            return {"error": "not found"}
        items = ProposalItem.query.filter_by(proposal_id=proposal.id).order_by(ProposalItem.position).all()
        html = render_template('proposal_pdf.html', proposal=proposal, items=items)
        # temp file
        out_filename = f"/tmp/proposal_{proposal.id}.pdf"
        # pdfkit config (wkhtmltopdf path)
        config = pdfkit.configuration(wkhtmltopdf=app.config.get('WKHTMLTOPDF_CMD'))
        options = {
            'enable-local-file-access': None,
            'margin-top': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'margin-right': '10mm'
        }
        pdfkit.from_string(html, out_filename, configuration=config, options=options)

        # Upload to S3 if configured
        s3_bucket = app.config.get('S3_BUCKET')
        if s3_bucket:
            s3 = boto3.client('s3',
                              region_name=app.config.get('S3_REGION'),
                              aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
            key = f"proposals/{proposal.id}/proposal.pdf"
            s3.upload_file(out_filename, s3_bucket, key, ExtraArgs={'ACL':'public-read', 'ContentType':'application/pdf'})
            pdf_url = f"https://{s3_bucket}.s3.{app.config.get('S3_REGION')}.amazonaws.com/{key}"
        else:
            # fallback to local static folder (dev)
            static_dir = os.path.join(app.root_path, '..', 'static', 'pdfs')
            os.makedirs(static_dir, exist_ok=True)
            dest = os.path.join(static_dir, f"proposal_{proposal.id}.pdf")
            os.replace(out_filename, dest)
            pdf_url = url_for('static', filename=f"pdfs/proposal_{proposal.id}.pdf", _external=True)

        proposal.pdf_url = pdf_url
        db.session.commit()
        return {"pdf_url": pdf_url}
