/***************************************************************************
    qgslabelengineconfigdialog.h
    ---------------------
    begin                : May 2010
    copyright            : (C) 2010 by Marco Hugentobler
    email                : marco dot hugentobler at sourcepole dot ch
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#ifndef QGSLABELENGINECONFIGDIALOG_H
#define QGSLABELENGINECONFIGDIALOG_H

#include <QDialog>

#include "ui_qgslabelengineconfigdialog.h"
#include "qgis_app.h"


class APP_EXPORT QgsLabelEngineConfigDialog : public QDialog, private Ui::QgsLabelEngineConfigDialog
{
    Q_OBJECT
  public:
    QgsLabelEngineConfigDialog( QWidget* parent = nullptr );

  public slots:
    void onOK();
    void setDefaults();

  protected:
};

#endif // QGSLABELENGINECONFIGDIALOG_H
