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

    @PostMapping("/generate/patients/excel")
    public ResponseEntity<byte[]> generateExcel(@RequestBody List<Map<String, Object>> patients) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Pacientes");

        // Header
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

        // Data
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

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("pacientes.xlsx").build());

        return new ResponseEntity<>(bos.toByteArray(), headers, HttpStatus.OK);
    }

    @PostMapping("/generate/doctors/excel")
    public ResponseEntity<byte[]> generateDoctorsExcel(@RequestBody List<Map<String, Object>> doctors) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Doctores");

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("DNI");
        header.createCell(1).setCellValue("Nombre");
        header.createCell(2).setCellValue("Apellido");
        header.createCell(3).setCellValue("Correo electrónico");
        header.createCell(4).setCellValue("Especialidad");

        int rowIdx = 1;
        for (Map<String, Object> doctor : doctors) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(doctor.getOrDefault("dni", "").toString());
            row.createCell(1).setCellValue(doctor.getOrDefault("first_name", "").toString());
            row.createCell(2).setCellValue(doctor.getOrDefault("last_name", "").toString());
            row.createCell(3).setCellValue(doctor.getOrDefault("email", "").toString());
            row.createCell(4).setCellValue(doctor.getOrDefault("specialty", "").toString());
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("doctores.xlsx").build());

        return new ResponseEntity<>(bos.toByteArray(), headers, HttpStatus.OK);
    }

    @PostMapping("/generate/appointments/excel")
    public ResponseEntity<byte[]> generateAppointmentsExcel(@RequestBody List<Map<String, Object>> appointments) throws Exception {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Citas");

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("Fecha");
        header.createCell(1).setCellValue("Hora");
        header.createCell(2).setCellValue("Estado");
        header.createCell(3).setCellValue("Motivo");
        header.createCell(4).setCellValue("Paciente");
        header.createCell(5).setCellValue("DNI Paciente");
        header.createCell(6).setCellValue("Doctor");
        header.createCell(7).setCellValue("DNI Doctor");

        int rowIdx = 1;
        for (Map<String, Object> appt : appointments) {
            Row row = sheet.createRow(rowIdx++);
            row.createCell(0).setCellValue(appt.getOrDefault("date", "").toString());
            row.createCell(1).setCellValue(appt.getOrDefault("time", "").toString());
            row.createCell(2).setCellValue(appt.getOrDefault("status", "").toString());
            row.createCell(3).setCellValue(appt.getOrDefault("reason", "").toString());
            row.createCell(4).setCellValue(
                appt.getOrDefault("patient_first_name", "") + " " + appt.getOrDefault("patient_last_name", "")
            );
            row.createCell(5).setCellValue(appt.getOrDefault("patient_dni", "").toString());
            row.createCell(6).setCellValue(
                appt.getOrDefault("doctor_first_name", "") + " " + appt.getOrDefault("doctor_last_name", "")
            );
            row.createCell(7).setCellValue(appt.getOrDefault("doctor_dni", "").toString());
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        workbook.write(bos);
        workbook.close();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("citas.xlsx").build());

        return new ResponseEntity<>(bos.toByteArray(), headers, HttpStatus.OK);
    }
}
