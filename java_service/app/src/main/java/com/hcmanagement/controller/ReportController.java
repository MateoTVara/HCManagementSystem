package com.hcmanagement.controller;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayOutputStream;
import java.util.List;
import java.util.Map;

@RestController
public class ReportController {

    @PostMapping("/generate/excel")
    public ResponseEntity<byte[]> generateExcel(@RequestBody List<Map<String, Object>> patients) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Pacientes");

        // Header
        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("DNI");
        header.createCell(1).setCellValue("Nombre");
        header.createCell(2).setCellValue("Apellido");
        header.createCell(3).setCellValue("Fecha de nacimiento");

        // Data
        int rowIdx = 1;
        for (Map<String, Object> patient : patients) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(patient.get("dni").toString());
            row.createCell(1).setCellValue(patient.get("first_name").toString());
            row.createCell(2).setCellValue(patient.get("last_name").toString());
            row.createCell(3).setCellValue(patient.get("date_of_birth").toString());
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("pacientes.xlsx").build());

        return new ResponseEntity<>(bos.toByteArray(), headers, HttpStatus.OK);
    }
}
