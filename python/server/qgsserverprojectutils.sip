/***************************************************************************
                              qgsserverprojectutils.sip
                              -------------------------
  begin                : December 19, 2016
  copyright            : (C) 2016 by Paul Blottiere
  email                : paul dot blottiere at oslandia dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

%ModuleHeaderCode
#include "qgsserverprojectutils.h"
%End

/** \ingroup server
 * The QgsServerProjectUtils namespace provides a way to retrieve specific
 * entries from a QgsProject.
 * @note added in QGIS 3.0
 */
namespace QgsServerProjectUtils
{
    /** Returns the maximum width for WMS images defined in a QGIS project.
      * @param project the QGIS project
      * @return width if defined in project, -1 otherwise.
      */
    int wmsMaxWidth( const QgsProject& project );

    /** Returns the maximum height for WMS images defined in a QGIS project.
      * @param project the QGIS project
      * @return height if defined in project, -1 otherwise.
      */
    int wmsMaxHeight( const QgsProject& project );

    /** Returns the WMS service url defined in a QGIS project.
      * @param project the QGIS project
      * @return url if defined in project, an empty string otherwise.
      */
    QString wmsServiceUrl( const QgsProject& project );

    /** Returns the WFS service url defined in a QGIS project.
      * @param project the QGIS project
      * @return url if defined in project, an empty string otherwise.
      */
    QString wfsServiceUrl( const QgsProject& project );

    /** Returns the WCS service url defined in a QGIS project.
      * @param project the QGIS project
      * @return url if defined in project, an empty string otherwise.
      */
    QString wcsServiceUrl( const QgsProject& project );
};
