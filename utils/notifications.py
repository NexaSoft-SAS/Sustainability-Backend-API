import os
import aiohttp
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

async def send_slack_notification(diagnostico_data: Dict) -> bool:
    """Send Slack notification when new diagnostico is created"""
    if not WEBHOOK_URL:
        logger.info("No webhook URL configured, skipping notification")
        return False
    
    try:
        # Format message for Slack
        message = {
            "text": "🚀 Nueva solicitud de Diagnóstico Verde",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🌱 Nueva Solicitud de Diagnóstico Verde"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Empresa:*\n{diagnostico_data['empresa']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Contacto:*\n{diagnostico_data['contacto_nombre']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Email:*\n{diagnostico_data['contacto_email']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Teléfono:*\n{diagnostico_data.get('telefono', 'No proporcionado')}"
                        }
                    ]
                }
            ]
        }
        
        if diagnostico_data.get('mensaje'):
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Mensaje:*\n{diagnostico_data['mensaje']}"
                }
            })
        
        message["blocks"].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Fuente: {diagnostico_data.get('fuente_trafico', 'web')} | Fecha: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
                }
            ]
        })
        
        # Send webhook
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=message) as response:
                if response.status == 200:
                    logger.info("Slack notification sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send Slack notification: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        return False

async def send_discord_notification(diagnostico_data: Dict) -> bool:
    """Send Discord notification when new diagnostico is created"""
    if not WEBHOOK_URL or 'discord' not in WEBHOOK_URL:
        return False
    
    try:
        # Format message for Discord
        embed = {
            "embeds": [
                {
                    "title": "🌱 Nueva Solicitud de Diagnóstico Verde",
                    "color": 0x10b981,  # Emerald green
                    "fields": [
                        {"name": "Empresa", "value": diagnostico_data['empresa'], "inline": True},
                        {"name": "Contacto", "value": diagnostico_data['contacto_nombre'], "inline": True},
                        {"name": "Email", "value": diagnostico_data['contacto_email'], "inline": False},
                    ],
                    "footer": {
                        "text": f"Fuente: {diagnostico_data.get('fuente_trafico', 'web')}"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        if diagnostico_data.get('telefono'):
            embed["embeds"][0]["fields"].append({
                "name": "Teléfono", 
                "value": diagnostico_data['telefono'], 
                "inline": True
            })
        
        if diagnostico_data.get('mensaje'):
            embed["embeds"][0]["fields"].append({
                "name": "Mensaje", 
                "value": diagnostico_data['mensaje'], 
                "inline": False
            })
        
        # Send webhook
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=embed) as response:
                if response.status in [200, 204]:
                    logger.info("Discord notification sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send Discord notification: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"Error sending Discord notification: {str(e)}")
        return False

async def send_notification(diagnostico_data: Dict) -> bool:
    """Send notification to configured webhook (auto-detect Slack or Discord)"""
    if not WEBHOOK_URL:
        return False
    
    if 'slack' in WEBHOOK_URL:
        return await send_slack_notification(diagnostico_data)
    elif 'discord' in WEBHOOK_URL:
        return await send_discord_notification(diagnostico_data)
    else:
        # Try Slack format by default
        return await send_slack_notification(diagnostico_data)