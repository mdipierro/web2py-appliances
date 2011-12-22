<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output indent="yes" method="xml" />
  <xsl:template match="/mysqldump/database">
    <xsl:comment> WWWSQLEditor XML import </xsl:comment>
    <sql>
      <xsl:for-each select="table_structure">

        <!--table id="0" title="location" x="757" y="612"-->
        <xsl:element name="table">
          <xsl:attribute name="id">
            <xsl:value-of select="position()-1"/>
          </xsl:attribute>
          <xsl:attribute name="title">
            <xsl:value-of select="@name"/>
          </xsl:attribute>
          <xsl:attribute name="x">
            <xsl:value-of select="concat(position()-1, '00')"/>
          </xsl:attribute>
          <xsl:attribute name="y">
            <xsl:value-of select="concat(position(), '00')"/>
          </xsl:attribute>

          <xsl:for-each select="field">

            <!--row id="0" pk="pk" index="index"-->
            <xsl:element name="row">
              <xsl:attribute name="id">
                <xsl:value-of select="position()-1"/>
              </xsl:attribute>
              <xsl:if test="@Null='YES'">
                <xsl:attribute name="nn">
                  <xsl:text>nn</xsl:text>
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="@Key='PRI'">
                <xsl:attribute name="pk">
                  <xsl:text>pk</xsl:text>
                </xsl:attribute>
                <xsl:attribute name="index">
                  <xsl:text>index</xsl:text>
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="contains(@Type, '(') and not(@Key='PRI')">
                <xsl:attribute name="special">
                  <xsl:value-of select="substring-before(substring-after(@Type, '('), ')')"/>
                </xsl:attribute>
              </xsl:if>
              
              <xsl:variable name="Type">
                <xsl:call-template name="dataType">
                  <xsl:with-param name="mysqlType">
                    <xsl:choose>
                      <xsl:when test="contains(@Type, '(')">
                        <xsl:value-of select="substring-before(@Type, '(')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="@Type"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:with-param>
                </xsl:call-template>
              </xsl:variable>
              
              <title>
                <xsl:value-of select="@Field"/>
              </title>
              <default>
                <xsl:choose>
                  <xsl:when test="string-length(@Default)>0">
                    <xsl:value-of select="@Default"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <!--xsl:if test="$Type='Integer'">0</xsl:if-->
                    <xsl:text>0</xsl:text>
                  </xsl:otherwise>
                </xsl:choose>
              </default>
              <type>
                <xsl:value-of select="$Type"/>
              </type>
            </xsl:element>
          </xsl:for-each>
        </xsl:element>
      </xsl:for-each>
    </sql>
  </xsl:template>

  <!-- Data types -->
  <xsl:template name="dataType">
    <xsl:param name="mysqlType"/>
    <xsl:choose>
      <!--xsl:when test="$mysqlType=''"></xsl:when-->
      <xsl:when test="substring($mysqlType, string-length($mysqlType)-2)='int'">Integer</xsl:when>
      <xsl:when test="substring($mysqlType, string-length($mysqlType)-3)='char'">String</xsl:when>
      <xsl:when test="substring($mysqlType, string-length($mysqlType)-3)='text'">Text</xsl:when>
      <xsl:when test="substring($mysqlType, string-length($mysqlType)-5)='binary'">Binary</xsl:when>
      <xsl:when test="substring($mysqlType, string-length($mysqlType)-2)='lob'">BLOB</xsl:when>
      <xsl:when test="$mysqlType='date'">Date</xsl:when>
      <xsl:otherwise>String</xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>