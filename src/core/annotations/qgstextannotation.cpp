/***************************************************************************
                              qgstextannotation.cpp
                              ------------------------
  begin                : February 9, 2010
  copyright            : (C) 2010 by Marco Hugentobler
  email                : marco dot hugentobler at hugis dot net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgstextannotation.h"
#include <QDomDocument>
#include <QPainter>

QgsTextAnnotation::QgsTextAnnotation( QObject* parent )
    : QgsAnnotation( parent )
    , mDocument( new QTextDocument( QString() ) )
{
  mDocument->setUseDesignMetrics( true );
}

const QTextDocument* QgsTextAnnotation::document() const
{
  return mDocument.get();
}

void QgsTextAnnotation::setDocument( const QTextDocument* doc )
{
  if ( doc )
    mDocument.reset( doc->clone() );
  else
    mDocument.reset();
  emit appearanceChanged();
}

void QgsTextAnnotation::renderAnnotation( QgsRenderContext& context, QSizeF size ) const
{
  QPainter* painter = context.painter();
  if ( !mDocument )
  {
    return;
  }

  mDocument->setTextWidth( size.width() );

  QRectF clipRect = QRectF( 0, 0, size.width(), size.height() );
  if ( painter->hasClipping() )
  {
    //QTextDocument::drawContents will draw text outside of the painter's clip region
    //when it is passed a clip rectangle. So, we need to intersect it with the
    //painter's clip region to prevent text drawn outside clipped region (e.g., outside composer maps, see #10400)
    clipRect = clipRect.intersected( painter->clipRegion().boundingRect() );
  }
  //draw text document
  mDocument->drawContents( painter, clipRect );
}

void QgsTextAnnotation::writeXml( QDomElement& elem, QDomDocument & doc ) const
{
  QDomElement annotationElem = doc.createElement( QStringLiteral( "TextAnnotationItem" ) );
  if ( mDocument )
  {
    annotationElem.setAttribute( QStringLiteral( "document" ), mDocument->toHtml() );
  }
  _writeXml( annotationElem, doc );
  elem.appendChild( annotationElem );
}

void QgsTextAnnotation::readXml( const QDomElement& itemElem, const QDomDocument& doc )
{
  mDocument.reset( new QTextDocument );
  mDocument->setHtml( itemElem.attribute( QStringLiteral( "document" ), QString() ) );
  QDomElement annotationElem = itemElem.firstChildElement( QStringLiteral( "AnnotationItem" ) );
  if ( !annotationElem.isNull() )
  {
    _readXml( annotationElem, doc );
  }
}
