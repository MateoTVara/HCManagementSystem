package com.hcmanagement.service;

import java.io.ByteArrayOutputStream;
import java.util.List;
import java.util.Map;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.*;

public class PatientExcelService {

    public byte[] generatePatientsExcel(List<Map<String, Object>> patients) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = (XSSFSheet)workbook.createSheet("Pacientes");

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("DNI");
        header.createCell(1).setCellValue("Nombre");
        header.createCell(2).setCellValue("Apellido");
        header.createCell(3).setCellValue("Fecha de nacimiento");
        header.createCell(4).setCellValue("Género");
        header.createCell(5).setCellValue("Tipo de sangre");
        header.createCell(6).setCellValue("Teléfono");
        header.createCell(7).setCellValue("Dirección");
        header.createCell(8).setCellValue("Correo electrónico");

        int rowIdx = 1;
        for (Map<String, Object> patient : patients) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(patient.getOrDefault("dni", "").toString());
            row.createCell(1).setCellValue(patient.getOrDefault("first_name", "").toString());
            row.createCell(2).setCellValue(patient.getOrDefault("last_name", "").toString());
            row.createCell(3).setCellValue(patient.getOrDefault("date_of_birth", "").toString());
            row.createCell(4).setCellValue(patient.getOrDefault("gender", "").toString());
            row.createCell(5).setCellValue(patient.getOrDefault("blood_type", "").toString());
            row.createCell(6).setCellValue(patient.getOrDefault("phone", "").toString());
            row.createCell(7).setCellValue(patient.getOrDefault("address", "").toString());
            row.createCell(8).setCellValue(patient.getOrDefault("email", "").toString());
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();

        return bos.toByteArray();
    }
    
}
